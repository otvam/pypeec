"""
Main script for solving a problem with the FFT-PEEC solver.
Check the input data, solve the problem, and parse the results.

The solver is implemented with NumPy and Scipy.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

from PyPEEC.lib_solver import check_data
from PyPEEC.lib_solver import voxel_geometry
from PyPEEC.lib_solver import green_function
from PyPEEC.lib_solver import problem_geometry
from PyPEEC.lib_solver import resistance_inductance
from PyPEEC.lib_solver import equation_system
from PyPEEC.lib_solver import equation_solver
from PyPEEC.lib_solver import extract_solution
from PyPEEC.lib_shared import logging_utils

# get a logger
logger = logging_utils.get_logger("solver")


def _run_check(data_voxel, data_problem):
    """
    Check and combine the input data.
    Exceptions are not caught inside this function.
    The different parts of the code are timed.
    """

    with logging_utils.BlockTimer(logger, "check_data"):
        # check the problem data
        check_data.check_problem(data_problem)

        # check the voxel data
        check_data.check_voxel(data_voxel)

        # combine the problem and voxel data
        data_solver = check_data.get_solver(data_voxel, data_problem)

    return data_solver


def _run_preproc(data_solver):
    """
    Compute the voxel geometry, Green functions, and the incidence matrix.
    The different parts of the code are timed.
    """

    # extract the input data
    n = data_solver["n"]
    d = data_solver["d"]
    n_green = data_solver["n_green"]

    # get the voxel geometry and the incidence matrix
    with logging_utils.BlockTimer(logger, "voxel_geometry"):
        # get the coordinate of the voxels
        xyz = voxel_geometry.get_voxel_coordinate(n, d)

        # compute the incidence matrix
        A_incidence = voxel_geometry.get_incidence_matrix(n)

    # get the Green functions
    with logging_utils.BlockTimer(logger, "green_function"):
        # Green function self-coefficient
        G_self = green_function.get_green_self(d)

        # Green function mutual coefficients
        G_mutual = green_function.get_green_tensor(n, d, n_green)

    # assemble results
    data_solver["xyz"] = xyz
    data_solver["A_incidence"] = A_incidence
    data_solver["G_self"] = G_self
    data_solver["G_mutual"] = G_mutual

    return data_solver


def _run_main(data_solver):
    """
    Construct and solve the problem (equation system).
    The different parts of the code are timed.
    """

    # extract the input data
    n = data_solver["n"]
    d = data_solver["d"]
    freq = data_solver["freq"]
    solver_options = data_solver["solver_options"]
    condition_options = data_solver["condition_options"]
    conductor_idx = data_solver["conductor_idx"]
    source_idx = data_solver["source_idx"]
    A_incidence = data_solver["A_incidence"]
    G_self = data_solver["G_self"]
    G_mutual = data_solver["G_mutual"]

    # parse the problem geometry (conductors and sources)
    with logging_utils.BlockTimer(logger, "problem_geometry"):
        # parse the conductors
        (idx_v, rho_v) = problem_geometry.get_conductor_geometry(conductor_idx)

        # parse the current sources
        (idx_src_c, I_src_c, G_src_c) = problem_geometry.get_source_current_geometry(source_idx)

        # parse the voltage sources
        (idx_src_v, V_src_v, R_src_v) = problem_geometry.get_source_voltage_geometry(source_idx)

        # reduce the incidence matrix to the non-empty voxels and compute face indices
        (A_reduced, idx_f) = problem_geometry.get_incidence_matrix(n, A_incidence, idx_v)

        # get a summary of the problem size
        problem_status = problem_geometry.get_status(n, idx_v, idx_f, idx_src_c, idx_src_v)

    # get the resistances and inductances
    with logging_utils.BlockTimer(logger, "resistance_inductance"):
        # get the resistance vector
        R_vector = resistance_inductance.get_resistance_vector(n, d, A_reduced, idx_f, rho_v)

        # get the inductance vector (preconditioner) and tensor (full problem, circulant tensor)
        (L_tensor, L_vector) = resistance_inductance.get_inductance_matrix(n, d, idx_f, G_mutual, G_self)

        # get the impedance vector (preconditioner) and tensor (full problem, FFT circulant tensor)
        (ZL_tensor, ZL_vector) = resistance_inductance.get_inductance_operator(freq, L_tensor, L_vector)

    # assemble the equation system
    with logging_utils.BlockTimer(logger, "equation_system"):
        # compute the right-hand vector with the sources
        rhs = equation_system.get_source_vector(idx_v, idx_f, I_src_c, V_src_v)

        # get the matrices defining the KCL, KVL
        (A_kvl, A_kcl) = equation_system.get_kvl_kcl_matrix(A_reduced, idx_f, idx_src_c, idx_src_v)

        # get the matrices the sources
        A_src = equation_system.get_source_matrix(idx_v, idx_src_c, idx_src_v, G_src_c, R_src_v)

        # get the linear operator for the preconditioner (guess of the inverse)
        pcd_op = equation_system.get_preconditioner_operator(idx_v, idx_f, idx_src_c, idx_src_v, A_kvl, A_kcl, A_src, R_vector, ZL_vector)

        # get the linear operator for the full system (matrix-vector multiplication)
        sys_op = equation_system.get_system_operator(n, idx_v, idx_f, idx_src_c, idx_src_v, A_kvl, A_kcl, A_src, R_vector, ZL_tensor)

        # get a matrix for detecting if the problem is quasi-singular (this matrix has no physical meaning)
        S_matrix = equation_system.get_singular(A_kvl, A_kcl, A_src, R_vector, ZL_vector)

    # solve the equation system
    with logging_utils.BlockTimer(logger, "equation_solver"):
        # estimate the condition number of the problem (to detect quasi-singular problem)
        (condition_ok, condition_status) = equation_solver.get_condition(S_matrix, condition_options)

        # solve the equation system
        (sol, solver_ok, solver_status) = equation_solver.get_solver(sys_op, pcd_op, rhs, solver_options)

        # compute converge
        has_converged = solver_ok and condition_ok

    # assemble results
    data_solver["idx_f"] = idx_f
    data_solver["idx_v"] = idx_v
    data_solver["rho_v"] = rho_v
    data_solver["idx_src_v"] = idx_src_v
    data_solver["idx_src_c"] = idx_src_c
    data_solver["problem_status"] = problem_status
    data_solver["sol"] = sol
    data_solver["has_converged"] = has_converged
    data_solver["solver_status"] = solver_status
    data_solver["condition_status"] = condition_status

    return data_solver


def _run_postproc(data_solver):
    """
    Extract the solution.
    The different parts of the code are timed.
    """

    # extract the input data
    n = data_solver["n"]
    d = data_solver["d"]
    source_idx = data_solver["source_idx"]
    A_incidence = data_solver["A_incidence"]
    idx_f = data_solver["idx_f"]
    idx_v = data_solver["idx_v"]
    idx_src_c = data_solver["idx_src_c"]
    idx_src_v = data_solver["idx_src_v"]
    sol = data_solver["sol"]

    # extract the solution
    with logging_utils.BlockTimer(logger, "extract_solution"):
        # split the solution vector to get the face currents, the voxel potentials, and the sources
        (I_f_all, V_v_all, I_src_c, I_src_v) = extract_solution.get_sol_extract(n, idx_f, idx_v, idx_src_c, idx_src_v, sol)

        # get the voxel current densities from the face currents
        J_v_all = extract_solution.get_current_density(n, d, A_incidence, I_f_all)

        # parse the terminal voltages and currents for the sources
        terminal = extract_solution.get_terminal(source_idx, V_v_all, I_src_c, I_src_v)

        # assign invalid values to the empty voxels
        (V_v, J_v) = extract_solution.get_assign_field(idx_v, V_v_all, J_v_all)

    # assemble results
    data_solver["terminal"] = terminal
    data_solver["V_v"] = V_v
    data_solver["J_v"] = J_v

    return data_solver


def _run_assemble(data_solver):
    """
    Assemble the output data from the different dict.
    """

    # assign results
    data_res = {
        "n": data_solver["n"],
        "d": data_solver["d"],
        "xyz": data_solver["xyz"],
        "idx_v": data_solver["idx_v"],
        "idx_src_c": data_solver["idx_src_c"],
        "idx_src_v": data_solver["idx_src_v"],
        "freq": data_solver["freq"],
        "has_converged": data_solver["has_converged"],
        "problem_status": data_solver["problem_status"],
        "solver_status": data_solver["solver_status"],
        "condition_status": data_solver["condition_status"],
        "rho_v": data_solver["rho_v"],
        "V_v": data_solver["V_v"],
        "J_v": data_solver["J_v"],
        "terminal": data_solver["terminal"],
    }

    return data_res


def run(data_voxel, data_problem):
    """
    Main script for solving a problem with the FFT-PEEC solver.
    Handle invalid data with exceptions.
    """

    # init
    logger.info("init")

    # check the input data
    try:
        data_solver = _run_check(data_voxel, data_problem)
    except check_data.CheckError as ex:
        logger.error(str(ex))
        return False, None

    # run the solver
    data_solver = _run_preproc(data_solver)
    data_solver = _run_main(data_solver)
    data_solver = _run_postproc(data_solver)
    data_res = _run_assemble(data_solver)

    # end message
    logger.info("successful termination")

    return True, data_res
