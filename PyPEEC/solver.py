"""
Main script for solving a problem with the FFT-PEEC solver.
Check the input data, solve the problem, and parse the results.
The different parts of the code are timed.

The solver is implemented with NumPy and Scipy.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

from PyPEEC.lib_solver import voxel_geometry
from PyPEEC.lib_solver import dense_matrix
from PyPEEC.lib_solver import problem_geometry
from PyPEEC.lib_solver import system_matrix
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
    green_simplify = data_solver["green_simplify"]
    coupling_simplify = data_solver["coupling_simplify"]

    # get the voxel geometry and the incidence matrix
    with timelogger.BlockTimer(logger, "voxel_geometry"):
        # get the coordinate of the voxels
        voxel_point = voxel_geometry.get_voxel_point(n, d, c)

        # compute the incidence matrix
        A_vox = voxel_geometry.get_incidence_matrix(n)

    # get the Green functions
    with timelogger.BlockTimer(logger, "dense_matrix"):
        # Green function self-coefficient
        G_self = dense_matrix.get_green_self(d)

        # Green function mutual coefficients
        G_mutual = dense_matrix.get_green_tensor(n, d, green_simplify)

        # Green function mutual coefficients
        K_tsr = dense_matrix.get_coupling_tensor(n, d, coupling_simplify)

    # assemble results
    data_solver["voxel_point"] = voxel_point
    data_solver["A_vox"] = A_vox
    data_solver["G_self"] = G_self
    data_solver["G_mutual"] = G_mutual
    data_solver["K_tsr"] = K_tsr

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
    material_idx = data_solver["material_idx"]
    source_idx = data_solver["source_idx"]
    A_vox = data_solver["A_vox"]
    G_self = data_solver["G_self"]
    G_mutual = data_solver["G_mutual"]
    K_tsr = data_solver["K_tsr"]

    # parse the problem geometry (conductors and sources)
    with timelogger.BlockTimer(logger, "problem_geometry"):
        # parse the conductors
        (idx_vc, rho_vc) = problem_geometry.get_material_geometry(material_idx, "conductor")
        (idx_vm, rho_vm) = problem_geometry.get_material_geometry(material_idx, "magnetic")

        # parse the sources
        (idx_src_c, I_src_c, G_src_c) = problem_geometry.get_source_geometry(source_idx, "current")
        (idx_src_v, V_src_v, R_src_v) = problem_geometry.get_source_geometry(source_idx, "voltage")

        # reduce the incidence matrix to the non-empty voxels and compute face indices
        (A_net_c, idx_fc) = problem_geometry.get_incidence_matrix(A_vox, idx_vc)
        (A_net_m, idx_fm) = problem_geometry.get_incidence_matrix(A_vox, idx_vm)

        # get a summary of the problem size
        problem_status = problem_geometry.get_status(n, idx_vc, idx_vm, idx_fc, idx_fm, idx_src_c, idx_src_v)

    # get the resistances and inductances
    with timelogger.BlockTimer(logger, "resistance_inductance"):
        # get the resistance vector
        R_vec_c = system_matrix.get_R_vector(n, d, A_net_c, idx_fc, rho_vc)
        R_vec_m = system_matrix.get_R_vector(n, d, A_net_m, idx_fm, rho_vm)

        # get the inductance tensor (preconditioner and full problem)
        (L_vec_c, L_tsr_c) = system_matrix.get_L_matrix(n, d, idx_fc, G_self, G_mutual)

        # get the potential tensor (preconditioner and full problem)
        (P_vec_m, P_tsr_m) = system_matrix.get_P_matrix(n, d, idx_vm, G_self, G_mutual)

        # prepare the matrices for multiplication (FFT circulant tensors or dense matrices)
        (L_op_c, P_op_m) = system_matrix.get_extract_matrix(idx_fc, idx_vm, L_tsr_c, P_tsr_m)

        # get the coupling matrices
        (K_op_c, K_op_m) = system_matrix.get_coupling_matrix(n, idx_vc, idx_vm, idx_fc, idx_fm, A_net_c, A_net_m, K_tsr)

    # assemble the equation system
    with timelogger.BlockTimer(logger, "equation_system"):
        # compute the right-hand vector with the sources
        rhs = equation_system.get_source_vector(idx_vc, idx_vm, idx_fc, idx_fm, I_src_c, V_src_v)

        # get the KVL and KCL connection matrices
        A_c = equation_system.get_kvl_kcl_matrix(A_net_c)
        A_m = equation_system.get_kvl_kcl_matrix(A_net_m)

        # get the source connection matrices
        A_src = equation_system.get_source_matrix(idx_vc, idx_vm, idx_src_c, idx_src_v, G_src_c, R_src_v)

        # get the linear operator for the preconditioner (guess of the inverse)
        (pcd_op, S_mat) = equation_system.get_cond_operator(freq, A_c, A_m, A_src, R_vec_c, R_vec_m, L_vec_c, P_vec_m)

        # get the linear operator for the full system (matrix-vector multiplication)
        sys_op = equation_system.get_system_operator(freq, A_c, A_m, A_src, R_vec_c, R_vec_m, L_op_c, P_op_m, K_op_c, K_op_m)

    # solve the equation system
    with timelogger.BlockTimer(logger, "equation_solver"):
        # estimate the condition number of the problem (to detect quasi-singular problem)
        (condition_ok, condition_status) = equation_solver.get_condition(S_mat, condition_options)

        # solve the equation system
        (sol, solver_ok, solver_status) = equation_solver.get_solver(sys_op, pcd_op, rhs, solver_options)

        # compute converge
        has_converged = solver_ok and condition_ok

    # assemble results
    data_solver["idx_fc"] = idx_fc
    data_solver["idx_fm"] = idx_fm
    data_solver["idx_vc"] = idx_vc
    data_solver["idx_vm"] = idx_vm
    data_solver["idx_src_v"] = idx_src_v
    data_solver["idx_src_c"] = idx_src_c
    data_solver["R_vec_c"] = R_vec_c
    data_solver["L_op_c"] = L_op_c
    data_solver["K_op_c"] = K_op_c
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
    A_vox = data_solver["A_vox"]
    source_idx = data_solver["source_idx"]
    idx_fc = data_solver["idx_fc"]
    idx_fm = data_solver["idx_fm"]
    idx_vc = data_solver["idx_vc"]
    idx_vm = data_solver["idx_vm"]
    idx_src_c = data_solver["idx_src_c"]
    idx_src_v = data_solver["idx_src_v"]
    R_vec_c = data_solver["R_vec_c"]
    L_op_c = data_solver["L_op_c"]
    K_op_c = data_solver["K_op_c"]
    sol = data_solver["sol"]

    # extract the solution
    with timelogger.BlockTimer(logger, "extract_solution"):
        # split the solution vector to get the face currents, the voxel potentials, and the sources
        (I_fc, I_fm, V_vc, V_vm, I_src) = extract_solution.get_sol_extract(idx_fc, idx_fm, idx_vc, idx_vm, idx_src_c, idx_src_v, sol)

        # get the voxel flow densities from the face flows
        J_vc = extract_solution.get_flow_density(n, d, idx_vc, idx_fc, A_vox, I_fc)
        B_vm = extract_solution.get_flow_density(n, d, idx_vm, idx_fm, A_vox, I_fm)

        # get the divergence of the face flows
        I_src_vc = extract_solution.get_flow_divergence(n, d, idx_vc, idx_fc, A_vox, I_fc)
        Q_src_vm = extract_solution.get_flow_divergence(n, d, idx_vm, idx_fm, A_vox, I_fm)

        # get the global quantities (energy and losses)
        integral = extract_solution.get_integral(I_fc, I_fm, R_vec_c, L_op_c, K_op_c)

        # extend the solution for the complete voxel structure (including the empty voxels)
        (V_v_all, I_src_c_all, I_src_v_all) = extract_solution.get_sol_extend(n, idx_src_c, idx_src_v, idx_vc, V_vc, I_src)

        # parse the terminal voltages and currents for the sources
        terminal = extract_solution.get_terminal(source_idx, V_v_all, I_src_c_all, I_src_v_all)

    # assemble results
    data_solver["terminal"] = terminal
    data_solver["integral"] = integral
    data_solver["V_vc"] = V_vc
    data_solver["V_vm"] = V_vm
    data_solver["J_vc"] = J_vc
    data_solver["B_vm"] = B_vm
    data_solver["I_src_vc"] = I_src_vc
    data_solver["Q_src_vm"] = Q_src_vm

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
        "idx_vc": data_solver["idx_vc"],
        "idx_vm": data_solver["idx_vm"],
        "idx_src_c": data_solver["idx_src_c"],
        "idx_src_v": data_solver["idx_src_v"],
        "freq": data_solver["freq"],
        "has_converged": data_solver["has_converged"],
        "problem_status": data_solver["problem_status"],
        "solver_status": data_solver["solver_status"],
        "condition_status": data_solver["condition_status"],
        "terminal": data_solver["terminal"],
        "integral": data_solver["integral"],
        "V_vc": data_solver["V_vc"],
        "V_vm": data_solver["V_vm"],
        "J_vc": data_solver["J_vc"],
        "B_vm": data_solver["B_vm"],
        "I_src_vc": data_solver["I_src_vc"],
        "Q_src_vm": data_solver["Q_src_vm"],
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
        The resistivity, potential, current density, and loss density of the different voxel are defined.
        The terminals quantities (voltage and current) of the sources are defined.
        The integral quantities (total losses and energy) of the problem are defined.
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
