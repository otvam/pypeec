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
    green_simplify = data_solver["green_simplify"]
    coupling_simplify = data_solver["coupling_simplify"]

    # get the voxel geometry and the incidence matrix
    with timelogger.BlockTimer(logger, "voxel_geometry"):
        # get the coordinate of the voxels
        voxel_point = voxel_geometry.get_voxel_point(n, d, c)

        # compute the incidence matrix
        A_inc = voxel_geometry.get_incidence_matrix(n)

    # get the Green functions
    with timelogger.BlockTimer(logger, "dense_matrix"):
        # Green function self-coefficient
        G_self = dense_matrix.get_green_self(d)

        # Green function mutual coefficients
        G_mutual = dense_matrix.get_green_tensor(n, d, green_simplify)

        # Green function mutual coefficients
        K_mutual = dense_matrix.get_coupling_tensor(n, d, coupling_simplify)

        import scipy.io as io
        io.savemat('tensor.mat', {"G": G_mutual, "K": K_mutual})

    # assemble results
    data_solver["voxel_point"] = voxel_point
    data_solver["A_inc"] = A_inc
    data_solver["G_self"] = G_self
    data_solver["G_mutual"] = G_mutual
    data_solver["K_mutual"] = K_mutual

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
    A_inc = data_solver["A_inc"]
    G_self = data_solver["G_self"]
    G_mutual = data_solver["G_mutual"]
    K_mutual = data_solver["K_mutual"]

    # parse the problem geometry (conductors and sources)
    with timelogger.BlockTimer(logger, "problem_geometry"):
        # parse the conductors
        (idx_vc, rho_vc) = problem_geometry.get_material_geometry(material_idx, "conductor")
        (idx_vm, rho_vm) = problem_geometry.get_material_geometry(material_idx, "magnetic")

        # parse the sources
        (idx_src_c, I_src_c, G_src_c) = problem_geometry.get_source_geometry(source_idx, "current")
        (idx_src_v, V_src_v, R_src_v) = problem_geometry.get_source_geometry(source_idx, "voltage")

        # reduce the incidence matrix to the non-empty voxels and compute face indices
        (A_red_c, idx_fc) = problem_geometry.get_incidence_matrix(A_inc, idx_vc)
        (A_red_m, idx_fm) = problem_geometry.get_incidence_matrix(A_inc, idx_vm)

        # get a summary of the problem size
        problem_status = problem_geometry.get_status(n, idx_vc, idx_vm, idx_fc, idx_fm, idx_src_c, idx_src_v)

    # get the resistances and inductances
    with timelogger.BlockTimer(logger, "resistance_inductance"):
        # get the resistance vector
        R_vec_c = resistance_inductance.get_R_vector(n, d, A_red_c, idx_fc, rho_vc)
        R_vec_m = resistance_inductance.get_R_vector(n, d, A_red_m, idx_fm, rho_vm)

        # get the inductance vector (preconditioner)
        L_vec_c = resistance_inductance.get_L_vector(n, d, idx_fc, G_self)

        # get the inductance tensor (full problem)
        L_tsr_c = resistance_inductance.get_L_matrix(n, d, G_mutual)

        # get the potential tensor (preconditioner and full problem)
        P_vec_m = resistance_inductance.get_P_vector(n, d, idx_vm, G_self)
        P_tsr_m = resistance_inductance.get_P_matrix(n, d, G_mutual)

    # assemble the equation system
    with timelogger.BlockTimer(logger, "equation_system"):
        # get the impedance vector (preconditioner) and tensor (full problem, FFT circulant tensor)
        # (ZL_tsr, ZL_vec) = equation_system.get_impedance_matrix(freq, idx_f, L_tsr, L_vec)

        import numpy as np
        import numpy.linalg as lna
        from PyPEEC.lib_matrix import matrix_multiply

        # get the angular frequency
        s = 1j*2*np.pi*freq

        mu = 4*np.pi*1e-7

        # compute the FFT circulant tensor (in order to make matrix-vector multiplication with FFT)
        L_tsr_c = mu*matrix_multiply.get_prepare_diag(idx_fc, L_tsr_c)
        Z_tsr_c = s*L_tsr_c
        P_tsr_m = (1/(mu*s))*matrix_multiply.get_prepare_single(idx_vm, P_tsr_m)
        R_vec_m = R_vec_m/(mu*s)

        vec = np.ones(len(idx_vm))
        iden = np.diag(vec)

        K_c = matrix_multiply.get_prepare_cross(idx_fc, idx_fm, K_mutual)
        K_m = matrix_multiply.get_prepare_cross(idx_fm, idx_fc, K_mutual)

        # compute the right-hand vector with the sources
        rhs = equation_system.get_source_vector(idx_vc, idx_vm, idx_fc, idx_fm, I_src_c, V_src_v)

        A_red_c = A_red_c.toarray()
        A_red_m = A_red_m.toarray()

        (A_kcl_src, A_src_pot, A_src_src) = equation_system.get_source_matrix(idx_vc, idx_src_c, idx_src_v, G_src_c, R_src_v)
        A_kcl_src = A_kcl_src.toarray()
        A_src_pot = A_src_pot.toarray()
        A_src_src = A_src_src.toarray()

        Z_c = np.diag(R_vec_c)+Z_tsr_c
        Z_m = np.diag(R_vec_m)

        (n_src, n_src) = A_src_src.shape

        a1 = np.zeros((len(idx_fc), len(idx_vm)))
        a2 = np.zeros((len(idx_fc), n_src))
        E1 = np.block([[+Z_c, +K_c, -1.0*A_red_c.transpose(), a1, a2]])

        a1 = np.zeros((len(idx_fm), len(idx_vc)))
        a2 = np.zeros((len(idx_fm), n_src))
        E2 = np.block([[-K_m, +Z_m, a1, -1.0*A_red_m.transpose(), a2]])

        a1 = np.zeros((len(idx_vm), len(idx_fc)))
        a2 = np.zeros((len(idx_vm), len(idx_vc)))
        a3 = np.zeros((len(idx_vm), n_src))
        E3 = np.block([[a1, np.matmul(P_tsr_m, A_red_m), a2, iden, a3]])

        a1 = np.zeros((len(idx_vc), len(idx_fm)))
        a2 = np.zeros((len(idx_vc), len(idx_vc)))
        a3 = np.zeros((len(idx_vc), len(idx_vm)))
        E4 = np.block([[A_red_c, a1, a2, a3, A_kcl_src]])

        a1 = np.zeros((n_src, len(idx_fc)))
        a2 = np.zeros((n_src, len(idx_fm)))
        a3 = np.zeros((n_src, len(idx_vm)))
        E5 = np.block([[a1, a2, A_src_pot, a3, A_src_src]])

        mat = np.concatenate((E1, E2, E3, E4, E5))

        sol = lna.solve(mat, rhs)

        sol_fc = sol[0:len(idx_fc)]
        sol_fm = sol[len(idx_fc):len(idx_fc)+len(idx_fm)]
        sol_vc = sol[len(idx_fc)+len(idx_fm):len(idx_fc)+len(idx_fm)+len(idx_vc)]
        sol_vm = sol[len(idx_fc)+len(idx_fm)+len(idx_vc):len(idx_fc)+len(idx_fm)+len(idx_vc)+len(idx_vm)]
        sol_src = sol[len(idx_fc)+len(idx_fm)+len(idx_vc)+len(idx_vm):len(idx_fc)+len(idx_fm)+len(idx_vc)+len(idx_vm)+n_src]

        idx = np.flatnonzero(idx_vc == idx_src_c)
        v = sol_vc[idx].item()
        L = np.imag(v)/(2*np.pi*freq)

        # get the energy for the different faces
        M_f = np.matmul(L_tsr_c, sol_fc)
        Mf_m = np.matmul(K_c, sol_fm)/s


        W_f = 0.5 * np.conj(sol_fc) * M_f
        W_tot = np.sum(np.real(W_f))
        print(2*W_tot)

        W_f = 0.5 * np.conj(sol_fc) * (M_f+Mf_m)
        W_tot = np.sum(np.real(W_f))
        print(2*W_tot)

        print(L)

        np.matmul(K_m, sol_fc)

        raise RunError("STOP")








        # get the matrices defining the KCL, KVL
        (A_kvl, A_kcl) = equation_system.get_kvl_kcl_matrix(A_red, idx_f, idx_src_c, idx_src_v)

        # get the matrices the sources
        A_src = equation_system.get_source_matrix(idx_v, idx_src_c, idx_src_v, G_src_c, R_src_v)

        # get the linear operator for the preconditioner (guess of the inverse)
        pcd_op = equation_system.get_preconditioner_operator(idx_v, idx_f, idx_src_c, idx_src_v, A_kvl, A_kcl, A_src, R_vec, ZL_vec)

        # get the linear operator for the full system (matrix-vector multiplication)
        sys_op = equation_system.get_system_operator(idx_v, idx_f, idx_src_c, idx_src_v, A_kvl, A_kcl, A_src, R_vec, ZL_tsr)

        # get a matrix for detecting if the problem is quasi-singular (this matrix has no physical meaning)
        S_mat = equation_system.get_singular(A_kvl, A_kcl, A_src, R_vec, ZL_vec)

    # solve the equation system
    with timelogger.BlockTimer(logger, "equation_solver"):
        # estimate the condition number of the problem (to detect quasi-singular problem)
        (condition_ok, condition_status) = equation_solver.get_condition(S_mat, condition_options)

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
    data_solver["R_vec"] = R_vec
    data_solver["L_tsr"] = L_tsr
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
    A_inc = data_solver["A_inc"]
    source_idx = data_solver["source_idx"]
    idx_f = data_solver["idx_f"]
    idx_v = data_solver["idx_v"]
    idx_src_c = data_solver["idx_src_c"]
    idx_src_v = data_solver["idx_src_v"]
    R_vec = data_solver["R_vec"]
    L_tsr = data_solver["L_tsr"]
    sol = data_solver["sol"]

    # extract the solution
    with timelogger.BlockTimer(logger, "extract_solution"):
        # split the solution vector to get the face currents, the voxel potentials, and the sources
        (I_f, V_v, I_src_c, I_src_v) = extract_solution.get_sol_extract(idx_f, idx_v, idx_src_c, idx_src_v, sol)

        # get the voxel current densities from the face currents
        J_v = extract_solution.get_current_density(n, d, idx_v, idx_f, A_inc, I_f)

        # get the resistive voltage drop and magnetic flux across the faces
        (V_f, M_f) = extract_solution.get_drop_flux(idx_f, R_vec, L_tsr, I_f)

        # get the global quantities (energy and losses)
        integral = extract_solution.get_integral(V_f, M_f, I_f)

        # get the voxel loss density
        P_v = extract_solution.get_loss(n, d, idx_v, idx_f, A_inc, V_f, I_f)

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
