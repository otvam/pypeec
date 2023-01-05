"""
Main script for solving a problem with the FFT-PEEC solver.
Check the input data, solve the problem, and parse the results.

The solver is implemented with NumPy and Scipy.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

from solver import check_data
from solver import voxel_geometry
from solver import green_function
from solver import problem_geometry
from solver import resistance_inductance
from solver import equation_system
from solver import equation_solver
from solver import extract_solution
from main import logging_utils

# get a logger
logger = logging_utils.get_logger("solver", "INFO")


def __run_check(data_solver):
    """
    Check the input data.
    Exceptions are not handled by this function.
    The different parts of the code are timed.
    """

    with logging_utils.BlockTimer(logger, "check_data"):
        # check the voxel structure
        check_data.check_data_solver(data_solver)

        # check the voxel structure
        check_data.check_voxel(data_solver)

        # check the solver options and frequency
        check_data.check_solver(data_solver)

        # check the conductors and sources
        check_data.check_problem(data_solver)


def __run_preproc(data_solver):
    """
    Compute the voxel geometry, Green functions, and the incidence matrix.
    The different parts of the code are timed.
    """

    # extract the input data
    n = data_solver["n"]
    d = data_solver["d"]
    ori = data_solver["ori"]
    n_green_simplify = data_solver["n_green_simplify"]

    # get the voxel geometry and the incidence matrix
    with logging_utils.BlockTimer(logger, "voxel_geometry"):
        # get the coordinate of the voxels
        xyz = voxel_geometry.get_voxel_coordinate(n, d, ori)

        # compute the incidence matrix
        A_incidence = voxel_geometry.get_incidence_matrix(n)

    # get the Green functions
    with logging_utils.BlockTimer(logger, "green_function"):
        # Green function self-coefficient
        G_self = green_function.get_green_self(d)

        # Green function mutual coefficients
        G_mutual = green_function.get_green_tensor(n, d, n_green_simplify)

    # assemble results
    data_preproc = {
        "xyz": xyz,
        "A_incidence": A_incidence,
        "G_self": G_self,
        "G_mutual": G_mutual,
    }

    return data_preproc


def __run_main(data_solver, data_preproc):
    """
    Construct and solve the problem (equation system).
    The different parts of the code are timed.
    """

    # extract the input data
    n = data_solver["n"]
    d = data_solver["d"]
    freq = data_solver["freq"]
    solver_options = data_solver["solver_options"]
    conductor = data_solver["conductor"]
    src_current = data_solver["src_current"]
    src_voltage = data_solver["src_voltage"]
    A_incidence = data_preproc["A_incidence"]
    G_self = data_preproc["G_self"]
    G_mutual = data_preproc["G_mutual"]

    # parse the problem geometry (conductors and sources)
    with logging_utils.BlockTimer(logger, "problem_geometry"):
        # parse the conductors
        (idx_v, rho_v) = problem_geometry.get_conductor_geometry(conductor)

        # parse the current and voltage sources
        (idx_src_c, val_src_c, idx_src_v, val_src_v) = problem_geometry.get_source_geometry(src_current, src_voltage)

        # reduce the incidence matrix to the non-empty voxels and compute face indices
        (A_reduced, idx_f_x, idx_f_y, idx_f_z, idx_f) = problem_geometry.get_incidence_matrix(n, A_incidence, idx_v)

        # compute the local (with respect to the non-empty voxels) indices for the sources
        (idx_voxel, idx_src_c_local, idx_src_v_local) = problem_geometry.get_source_index(n, idx_v, idx_src_c, idx_src_v)

        # get a summary of the problem size
        problem_status = problem_geometry.get_status(n, idx_v, idx_f, idx_src_c, idx_src_v)

    # display status
    logger.info("problem size: n_total = %d" % problem_status["n_total"])
    logger.info("problem size: n_conductor = %d" % problem_status["n_conductor"])
    logger.info("problem size: n_faces = %d" % problem_status["n_faces"])
    logger.info("problem size: n_src = %d" % problem_status["n_src"])
    logger.info("problem size: ratio_conductor = %.3e" % problem_status["ratio_conductor"])
    logger.info("problem size: ratio_src = %.3e" % problem_status["ratio_src"])

    # get the resistances and inductances
    with logging_utils.BlockTimer(logger, "resistance_inductance"):
        # get the resistivity for all the voxels (including empty voxels).
        rho_voxel = resistance_inductance.get_resistivity_vector(n, idx_v, rho_v)

        # get the resistance vector (preconditioner) and tensor (full problem, tensor)
        (R_tensor, R_vector) = resistance_inductance.get_resistance_matrix(n, d, idx_f_x, idx_f_y, idx_f_z, idx_f, rho_voxel)

        # get the inductance vector (preconditioner) and tensor (full problem, circulant tensor)
        (L_tensor, L_vector) = resistance_inductance.get_inductance_matrix(n, d, idx_f, G_mutual, G_self)

        # get the impedance vector (preconditioner) and tensor (full problem, FFT circulant tensor)
        (ZL_tensor, ZL_vector) = resistance_inductance.get_inductance_operator(n, freq, L_tensor, L_vector)

    # assemble the equation system
    with logging_utils.BlockTimer(logger, "equation_system"):
        # get the matrices defining the KCL, KVL, and sources
        (A_kcl, A_kvl, A_src) = equation_system.get_connection_matrix(A_reduced, idx_v, idx_f, idx_src_v_local)

        # compute the right-hand vector with the sources
        rhs = equation_system.get_source_vector(idx_v, idx_f, idx_src_c_local, val_src_c, val_src_v)

        # get the linear operator for the preconditioner (guess of the inverse)
        pcd_op = equation_system.get_preconditioner_operator(idx_v, idx_f, idx_src_v_local, A_kcl, A_kvl, A_src, R_vector, ZL_vector)

        # get the linear operator for the full system (matrix-vector multiplication)
        sys_op = equation_system.get_system_operator(n, idx_v, idx_f, idx_src_v_local, A_kcl, A_kvl, A_src, R_tensor, ZL_tensor)

        # get a matrix for detecting if the problem is quasi-singular (this matrix has no physical meaning)
        S_matrix = equation_system.get_singular(A_kcl, A_kvl, A_src)

    # solve the equation system
    with logging_utils.BlockTimer(logger, "equation_solver"):
        # estimate the condition number of the problem (to detect quasi-singular problem)
        cond = equation_solver.get_condition(S_matrix)

        # solve the equation system
        (sol, has_converged, solver_status) = equation_solver.get_solver(sys_op, pcd_op, rhs, cond, solver_options)

    # display status
    logger.info("matrix solver: n_dof = %d" % solver_status["n_dof"])
    logger.info("matrix solver: n_iter = %d" % solver_status["n_iter"])
    logger.info("matrix solver: cond = %.3e" % solver_status["cond"])
    logger.info("matrix solver: res_abs = %.3e" % solver_status["res_abs"])
    logger.info("matrix solver: res_rel = %.3e" % solver_status["res_rel"])
    logger.info("matrix solver: cond_ok = %s" % solver_status["cond_ok"])
    logger.info("matrix solver: solver_ok = %s" % solver_status["solver_ok"])
    if has_converged:
        logger.info("matrix solver: convergence achieved")
    else:
        logger.warning("matrix solver: convergence issues")

    # assemble results
    data_main = {
        "idx_f": idx_f,
        "idx_v": idx_v,
        "idx_src_v": idx_src_v,
        "problem_status": problem_status,
        "idx_voxel": idx_voxel,
        "rho_voxel": rho_voxel,
        "sol": sol,
        "has_converged": has_converged,
        "solver_status": solver_status,
    }

    return data_main


def __run_postproc(data_solver, data_preproc, data_main):
    """
    Extract the solution.
    The different parts of the code are timed.
    """

    # extract the input data
    n = data_solver["n"]
    d = data_solver["d"]
    src_current = data_solver["src_current"]
    src_voltage = data_solver["src_voltage"]
    A_incidence = data_preproc["A_incidence"]
    idx_f = data_main["idx_f"]
    idx_v = data_main["idx_v"]
    idx_src_v = data_main["idx_src_v"]
    sol = data_main["sol"]

    # extract the solution
    with logging_utils.BlockTimer(logger, "extract_solution"):
        # split the solution vector to get the face currents, the voxel potentials, and the sources
        (I_face, V_voxel, I_src_v) = extract_solution.get_sol_extract(n, idx_f, idx_v, idx_src_v, sol)

        # get the voxel current densities from the face currents
        J_voxel = extract_solution.get_current_density(n, d, A_incidence, I_face)

        # parse the terminal voltages and currents for the sources
        src_terminal = extract_solution.get_src_terminal(src_current, src_voltage, V_voxel, I_src_v)

        # assign invalid values to the empty voxels
        (V_voxel, J_voxel) = extract_solution.get_assign_field(n, idx_v, V_voxel, J_voxel)

    # assemble results
    data_postproc = {
        "src_terminal": src_terminal,
        "V_voxel": V_voxel,
        "J_voxel": J_voxel,
    }

    return data_postproc


def __run_assemble(data_solver, data_preproc, data_main, data_postproc):
    """
    Assemble the output data from the different dict.
    """

    # assign results
    data_res = {
        "n": data_solver["n"],
        "d": data_solver["d"],
        "ori": data_solver["ori"],
        "freq": data_solver["freq"],
        "xyz": data_preproc["xyz"],
        "idx_voxel": data_main["idx_voxel"],
        "rho_voxel": data_main["rho_voxel"],
        "has_converged": data_main["has_converged"],
        "problem_status": data_main["problem_status"],
        "solver_status": data_main["solver_status"],
        "V_voxel": data_postproc["V_voxel"],
        "J_voxel": data_postproc["J_voxel"],
        "src_terminal": data_postproc["src_terminal"],
    }

    return data_res


def run(data_solver):
    """
    Main script for solving a problem with the FFT-PEEC solver.
    Handle invalid data with exceptions.
    """

    # init
    logger.info("INIT")

    # run the solver
    try:
        __run_check(data_solver)
        data_preproc = __run_preproc(data_solver)
        data_main = __run_main(data_solver, data_preproc)
        data_postproc = __run_postproc(data_solver, data_preproc, data_main)
        data_res = __run_assemble(data_solver, data_preproc, data_main, data_postproc)

        status = True
        logger.info("successful termination")
    except check_data.CheckError as ex:
        data_res = None
        status = False
        logger.error(str(ex))

    # end
    logger.info("END")

    return status, data_res
