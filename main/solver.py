"""
Main script for solving a problem with the FFT-PEEC solver.
Check the input data, solve the problem, and parse the results.
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
logger = logging_utils.get_logger("solver")


def _run_sub(data_solver):
    """
    Solve a problem with the FFT-PEEC solver.
    Check the input data, solve the problem, and parse the results.
    Exceptions are not handled by this function.
    The different parts of the code are timed.
    """

    # check the input data type
    assert isinstance(data_solver, dict), "invalid input data"

    # check and extract the input data
    with logging_utils.BlockTimer(logger, "check_data"):
        # check the voxel structure
        (n, d, n_green_simplify) = check_data.check_voxel(data_solver)

        # check the solver options and frequency
        (freq, solver_options) = check_data.check_solver(data_solver)

        # check the conductors and sources
        (conductor, src_current, src_voltage) = check_data.check_problem(data_solver)

    # get the voxel geometry and the incidence matrix
    with logging_utils.BlockTimer(logger, "voxel_geometry"):
        # get the coordinate of the voxels
        xyz = voxel_geometry.get_voxel_coordinate(d, n)

        # compute the incidence matrix
        A_incidence = voxel_geometry.get_incidence_matrix(n)

    # get the Green functions
    with logging_utils.BlockTimer(logger, "green_function"):
        # Green function self-coefficient
        G_self = green_function.get_green_self(d)

        # Green function mutual coefficients
        G_mutual = green_function.get_green_tensor(d, n, n_green_simplify)

    # parse the problem geometry (conductors and sources)
    with logging_utils.BlockTimer(logger, "problem_geometry"):
        # parse the conductors
        (idx_v, rho_v) = problem_geometry.get_conductor_geometry(conductor)

        # parse the current and voltage sources
        (idx_src_c, val_src_c, idx_src_v, val_src_v) = problem_geometry.get_source_geometry(src_current, src_voltage)

        # reduce the incidence matrix to the non-empty voxels and compute face indices
        (A_reduced, idx_f_x, idx_f_y, idx_f_z, idx_f) = problem_geometry.get_incidence_matrix(n, A_incidence, idx_v)

        # compute the local (with respect to the non-empty voxels) indices for the sources
        (idx_src_c_local, idx_src_v_local) = problem_geometry.get_source_index(n, idx_v, idx_src_c, idx_src_v)

        # get a summary of the problem size
        problem_status = problem_geometry.get_status(n, idx_v, idx_f, idx_src_c, idx_src_v)

    # get the resistances and inductances
    with logging_utils.BlockTimer(logger, "resistance_inductance"):
        # get the resistance vector (preconditioner) and tensor (full problem, tensor)
        (R_tensor, R_vector) = resistance_inductance.get_resistance_matrix(n, d, idx_v, rho_v, idx_f_x, idx_f_y, idx_f_z, idx_f)

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

    # extract the solution
    with logging_utils.BlockTimer(logger, "extract_solution"):
        # split the solution vector to get the face currents, the voxel potentials, and the sources
        (I_face, V_voxel, I_src_v) = extract_solution.get_sol_extract(n, idx_f, idx_v, idx_src_v, sol)

        # get the voxel current densities from the face currents
        J_voxel = extract_solution.get_current_density(n, d, A_incidence, I_face)

        # parse the terminal voltages and currents for the sources
        src_terminal = extract_solution.get_src_terminal(src_current, src_voltage, V_voxel, I_src_v)

    # check convergence
    if has_converged:
        logger.info("convergence achieved")
    else:
        logger.warning("convergence issues")

    # assign results
    data_res = {
        "has_converged": has_converged,
        "problem_status": problem_status,
        "solver_status": solver_status,
        "src_terminal": src_terminal,
        "xyz": xyz,
        "V_voxel": V_voxel,
        "J_voxel": J_voxel,
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
        data_res = _run_sub(data_solver)
        status = True
        logger.info("successful termination")
    except check_data.CheckError as ex:
        status = False
        data_res = None
        logger.error(str(ex))

    # end
    logger.info("END")

    return status, data_res
