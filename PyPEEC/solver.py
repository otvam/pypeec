"""
Main script for solving a problem with the FFT-PEEC solver.
Check the input data, solve the problem, and parse the results.
The different parts of the code are timed.

The solver is implemented with NumPy and Scipy.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

from PyPEEC.lib_solver import voxel_geometry
from PyPEEC.lib_solver import green_function
from PyPEEC.lib_solver import problem_geometry
from PyPEEC.lib_solver import resistance_inductance
from PyPEEC.lib_solver import equation_system
from PyPEEC.lib_solver import equation_solver
from PyPEEC.lib_solver import extract_solution
from PyPEEC.lib_check import check_data_problem
from PyPEEC.lib_check import check_data_solver
from PyPEEC.lib_utils import timelogger
from PyPEEC.lib_utils.error import CheckError, RunError

# get a logger
logger = timelogger.get_logger("SOLVER")


def _run_preproc(data_solver):
    """
    Compute the voxel geometry, Green functions, and the incidence matrix.
    """

    # extract the data
    n = data_solver["n"]
    d = data_solver["d"]
    c = data_solver["c"]
    n_green = data_solver["n_green"]

    # get the voxel geometry and the incidence matrix
    with timelogger.BlockTimer(logger, "voxel_geometry"):
        # get the coordinate of the voxels
        voxel_point = voxel_geometry.get_voxel_point(n, d, c)

        # compute the incidence matrix
        A_incidence = voxel_geometry.get_incidence_matrix(n)

    # get the Green functions
    with timelogger.BlockTimer(logger, "green_function"):
        # Green function self-coefficient
        G_self = green_function.get_green_self(d)

        # Green function mutual coefficients
        G_mutual = green_function.get_green_tensor(n, d, n_green)

    # assemble results
    data_solver["voxel_point"] = voxel_point
    data_solver["A_incidence"] = A_incidence
    data_solver["G_self"] = G_self
    data_solver["G_mutual"] = G_mutual

    return data_solver


def _run_main(data_solver):
    """
    Construct and solve the problem (equation system).
    """

    # extract the data
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
    with timelogger.BlockTimer(logger, "problem_geometry"):
        # parse the conductors
        (idx_v, rho_v) = problem_geometry.get_conductor_geometry(conductor_idx)

        # parse the current sources
        (idx_src_c, I_src_c, G_src_c) = problem_geometry.get_source_current_geometry(source_idx)

        # parse the voltage sources
        (idx_src_v, V_src_v, R_src_v) = problem_geometry.get_source_voltage_geometry(source_idx)

        # reduce the incidence matrix to the non-empty voxels and compute face indices
        (A_reduced, idx_f) = problem_geometry.get_incidence_matrix(A_incidence, idx_v)

        # get a summary of the problem size
        problem_status = problem_geometry.get_status(n, idx_v, idx_f, idx_src_c, idx_src_v)

    # get the resistances and inductances
    with timelogger.BlockTimer(logger, "resistance_inductance"):
        # get the resistance vector
        R_vector = resistance_inductance.get_resistance_vector(n, d, A_reduced, idx_f, rho_v)

        # get the inductance vector (preconditioner) and tensor (full problem, circulant tensor)
        (L_tensor, L_vector) = resistance_inductance.get_inductance_matrix(n, d, idx_f, G_mutual, G_self)

    # assemble the equation system
    with timelogger.BlockTimer(logger, "equation_system"):
        # get the impedance vector (preconditioner) and tensor (full problem, FFT circulant tensor)
        (ZL_tensor, ZL_vector) = equation_system.get_impedance_matrix(freq, L_tensor, L_vector)

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
    with timelogger.BlockTimer(logger, "equation_solver"):
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
    data_solver["R_vector"] = R_vector
    data_solver["L_tensor"] = L_tensor
    data_solver["problem_status"] = problem_status
    data_solver["has_converged"] = has_converged
    data_solver["solver_status"] = solver_status
    data_solver["condition_status"] = condition_status
    data_solver["sol"] = sol

    return data_solver


def _run_postproc(data_solver):
    """
    Extract and parse the solution.
    """

    # extract the data
    n = data_solver["n"]
    d = data_solver["d"]
    A_incidence = data_solver["A_incidence"]
    source_idx = data_solver["source_idx"]
    idx_f = data_solver["idx_f"]
    idx_v = data_solver["idx_v"]
    idx_src_c = data_solver["idx_src_c"]
    idx_src_v = data_solver["idx_src_v"]
    R_vector = data_solver["R_vector"]
    L_tensor = data_solver["L_tensor"]
    sol = data_solver["sol"]

    # extract the solution
    with timelogger.BlockTimer(logger, "extract_solution"):
        # split the solution vector to get the face currents, the voxel potentials, and the sources
        (I_f, V_v, I_src_c, I_src_v) = extract_solution.get_sol_extract(idx_f, idx_v, idx_src_c, idx_src_v, sol)

        # get the voxel current densities from the face currents
        J_v = extract_solution.get_current_density(n, d, idx_v, idx_f, A_incidence, I_f)

        # get the voxel loss and energy densities from the currents and the resistance vector
        (P_v, W_v, integral) = extract_solution.get_loss_energy(n, d, idx_v, idx_f, A_incidence, R_vector, L_tensor, I_f)

        # extend the solution for the complete voxel structure (including the empty voxels)
        (V_v_all, I_src_c_all, I_src_v_all) = extract_solution.get_sol_extend(n, idx_v, idx_src_c, idx_src_v, V_v, I_src_c, I_src_v)

        # parse the terminal voltages and currents for the sources
        terminal = extract_solution.get_terminal(source_idx, V_v_all, I_src_c_all, I_src_v_all)

    # assemble results
    data_solver["terminal"] = terminal
    data_solver["integral"] = integral
    data_solver["V_v"] = V_v
    data_solver["J_v"] = J_v
    data_solver["P_v"] = P_v
    data_solver["W_v"] = W_v

    return data_solver


def _run_assemble(data_solver):
    """
    Generate the output data, discard intermediate results.
    """

    # assign results
    data_solution = {
        "n": data_solver["n"],
        "d": data_solver["d"],
        "c": data_solver["c"],
        "voxel_point": data_solver["voxel_point"],
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
        "P_v": data_solver["P_v"],
        "W_v": data_solver["W_v"],
        "terminal": data_solver["terminal"],
    }

    return data_solution


def run(data_voxel, data_problem):
    """
    Main script for solving a problem with the FFT-PEEC solver.
    Handle invalid data with exceptions.

    Parameters
    ----------
    data_voxel :  dict
        The dict describes the voxel structure.
        The voxel grid (number, size, and origin) is defined.
        Different domains (with the indices of the voxel) are defined.
        The connected components of the graph defined by the voxel structure are defined.
    data_problem: dict
        The dict describes the problem to be solved.
        The numerical options are defined.
        The frequency of the problem is defined.
        The resistivity of the different domain is defined.
        The current and voltage sources are defined.

    Returns
    -------
    status : boolean
        True if the call is successful.
        False if the problems are encountered
    data_solution: dict
        The dict describes the problem solution.
        The voxel structure is defined.
        The frequency of the problem is defined.
        The status of the solution (solver convergence and condition number) is described.
        The resistivity, potential, and current density of the different voxel is defined.
        The terminals quantities (voltage and current) of the sources are defined.
    """

    # run the solver
    try:
        # check the problem data
        check_data_problem.check_data_problem(data_problem)

        # combine the problem and voxel data
        data_solver = check_data_solver.get_data_solver(data_voxel, data_problem)

        # prepare the problem
        data_solver = _run_preproc(data_solver)

        # solve the problem
        data_solver = _run_main(data_solver)

        # extrac the solution
        data_solver = _run_postproc(data_solver)

        # assemble the output data structure
        data_solution = _run_assemble(data_solver)
    except (CheckError, RunError) as ex:
        timelogger.log_exception(logger, ex)
        return False, None, ex

    # end message
    logger.info("successful termination")

    return True, data_solution, None
