"""
Main script for solving a problem with the PEEC solver.
Check the input data, solve the problem, and parse the results.
The different parts of the code are timed.

The solver is implemented with NumPy and Scipy.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

from pypeec.lib_solver import sweep_solver
from pypeec.lib_solver import voxel_geometry
from pypeec.lib_solver import system_tensor
from pypeec.lib_solver import problem_geometry
from pypeec.lib_solver import problem_value
from pypeec.lib_solver import system_matrix
from pypeec.lib_solver import equation_system
from pypeec.lib_solver import equation_solver
from pypeec.lib_solver import extract_solution
from pypeec.lib_check import check_data_problem
from pypeec.lib_check import check_data_tolerance
from pypeec.lib_check import check_data_solver
from pypeec.lib_utils import timelogger
from pypeec.error import CheckError, RunError

# get a logger
LOGGER = timelogger.get_logger("SOLVER")


def _run_solver_init(data_solver):
    """
    Compute the voxel geometry, Green functions, and the incidence matrix.
    """

    # extract the data
    n = data_solver["n"]
    d = data_solver["d"]
    c = data_solver["c"]
    green_simplify = data_solver["green_simplify"]
    coupling_simplify = data_solver["coupling_simplify"]
    has_coupling = data_solver["has_coupling"]
    has_electric = data_solver["has_electric"]
    has_magnetic = data_solver["has_magnetic"]
    material_idx = data_solver["material_idx"]
    source_idx = data_solver["source_idx"]

    # get the voxel geometry and the incidence matrix
    with timelogger.BlockTimer(LOGGER, "voxel_geometry"):
        # get the coordinate of the voxels
        pts_vox = voxel_geometry.get_voxel_coordinate(n, d, c)

        # compute the incidence matrix
        A_vox = voxel_geometry.get_incidence_matrix(n)

    # get the Green functions
    with timelogger.BlockTimer(LOGGER, "system_tensor"):
        # Green function self-coefficient
        G_self = system_tensor.get_green_self(d)

        # Green function mutual coefficients
        G_mutual = system_tensor.get_green_tensor(n, d, green_simplify)

        # Green function mutual coefficients
        K_tsr = system_tensor.get_coupling_tensor(n, d, coupling_simplify, has_coupling)

    # parse the problem geometry (materials and sources)
    with timelogger.BlockTimer(LOGGER, "problem_geometry"):
        # parse the materials
        idx_vc = problem_geometry.get_material_indices(material_idx, "electric")
        idx_vm = problem_geometry.get_material_indices(material_idx, "magnetic")

        # parse the sources
        idx_src_c = problem_geometry.get_source_indices(source_idx, "current")
        idx_src_v = problem_geometry.get_source_indices(source_idx, "voltage")

        # reduce the incidence matrix to the non-empty voxels and compute face indices
        (pts_net_c, A_net_c, idx_fc) = problem_geometry.get_reduce_matrix(pts_vox, A_vox, idx_vc)
        (pts_net_m, A_net_m, idx_fm) = problem_geometry.get_reduce_matrix(pts_vox, A_vox, idx_vm)

        # free memory
        del pts_vox
        del A_vox

        # get a summary of the problem size
        problem_status = problem_geometry.get_status(n, idx_vc, idx_vm, idx_fc, idx_fm, idx_src_c, idx_src_v)

    # get the system operators
    with timelogger.BlockTimer(LOGGER, "system_matrix"):
        # get the inductance tensor (preconditioner and full problem)
        (L_c, L_op_c) = system_matrix.get_inductance_matrix(n, d, idx_fc, G_self, G_mutual, has_electric)

        # get the potential tensor (preconditioner and full problem)
        (P_m, P_op_m) = system_matrix.get_potential_matrix(d, idx_vm, G_self, G_mutual, has_magnetic)

        # free memory
        del G_self
        del G_mutual

        # get the coupling matrices
        (K_op_c, K_op_m) = system_matrix.get_coupling_matrix(n, idx_vc, idx_vm, idx_fc, idx_fm, A_net_c, A_net_m, K_tsr, has_coupling)

        # free memory
        del K_tsr

    # assign the results (will be merged in the solver output)
    data_init = {
        "n": n,
        "d": d,
        "c": c,
        "idx_vc": idx_vc,
        "idx_vm": idx_vm,
        "idx_fc": idx_fc,
        "idx_fm": idx_fm,
        "idx_src_c": idx_src_c,
        "idx_src_v": idx_src_v,
        "pts_net_c": pts_net_c,
        "pts_net_m": pts_net_m,
        "problem_status": problem_status,
    }

    # assign the results (internal data required to solve the problem)
    data_internal = {
        "A_net_c": A_net_c,
        "A_net_m": A_net_m,
        "L_c": L_c,
        "L_op_c": L_op_c,
        "P_m": P_m,
        "P_op_m": P_op_m,
        "K_op_c": K_op_c,
        "K_op_m": K_op_m,
    }

    return data_init, data_internal


def _run_solver_sweep(data_solver, data_init, data_internal, sweep_param, sol_init):
    """
    Create the equation system, solve the system, and extract the solution.
    """

    # extract the data
    n = data_solver["n"]
    d = data_solver["d"]
    material_idx = data_solver["material_idx"]
    source_idx = data_solver["source_idx"]
    condition_options = data_solver["condition_options"]
    solver_options = data_solver["solver_options"]

    # extract the data
    idx_vc = data_init["idx_vc"]
    idx_vm = data_init["idx_vm"]
    idx_fc = data_init["idx_fc"]
    idx_fm = data_init["idx_fm"]
    idx_src_c = data_init["idx_src_c"]
    idx_src_v = data_init["idx_src_v"]

    # extract the data
    A_net_c = data_internal["A_net_c"]
    A_net_m = data_internal["A_net_m"]
    L_c = data_internal["L_c"]
    L_op_c = data_internal["L_op_c"]
    P_m = data_internal["P_m"]
    P_op_m = data_internal["P_op_m"]
    K_op_c = data_internal["K_op_c"]
    K_op_m = data_internal["K_op_m"]

    # extract the data
    freq = sweep_param["freq"]
    material_val = sweep_param["material_val"]
    source_val = sweep_param["source_val"]

    # get the material and source values
    with timelogger.BlockTimer(LOGGER, "problem_value"):
        # parse the material parameters
        rho_vc = problem_value.get_material_values(material_val, material_idx, "electric")
        rho_vm = problem_value.get_material_values(material_val, material_idx, "magnetic")

        # parse the source parameters
        (I_src_c, G_src_c) = problem_value.get_source_values(source_val, source_idx, "current")
        (V_src_v, R_src_v) = problem_value.get_source_values(source_val, source_idx, "voltage")

        # get the resistance vector
        R_c = problem_value.get_resistance_vector(n, d, A_net_c, idx_fc, rho_vc)
        R_m = problem_value.get_resistance_vector(n, d, A_net_m, idx_fm, rho_vm)

    # assemble the equation system
    with timelogger.BlockTimer(LOGGER, "equation_system"):
        # compute the right-hand vector with the sources
        rhs = equation_system.get_source_vector(idx_vc, idx_vm, idx_fc, idx_fm, I_src_c, V_src_v)

        # get the source connection matrices
        A_src = equation_system.get_source_matrix(idx_vc, idx_src_c, idx_src_v, G_src_c, R_src_v)

        # get the linear operator for the preconditioner (guess of the inverse)
        (pcd_op, S_mat_c, S_mat_m) = equation_system.get_cond_operator(freq, A_net_c, A_net_m, A_src, R_c, R_m, L_c, P_m)

        # get the linear operator for the full system (matrix-vector multiplication)
        sys_op = equation_system.get_system_operator(freq, A_net_c, A_net_m, A_src, R_c, R_m, L_op_c, P_op_m, K_op_c, K_op_m)

    # solve the equation system
    with timelogger.BlockTimer(LOGGER, "equation_solver"):
        # estimate the condition number of the problem (to detect quasi-singular problem)
        (condition_ok, condition_status) = equation_solver.get_condition(S_mat_c, S_mat_m, condition_options)

        # free memory
        del S_mat_c
        del S_mat_m

        # solve the equation system
        (sol, res, conv, solver_ok, solver_status) = equation_solver.get_solver(sol_init, sys_op, pcd_op, rhs, solver_options)

        # free memory
        del pcd_op
        del sys_op

        # compute convergence
        has_converged = solver_ok and condition_ok

    # extract the solution
    with timelogger.BlockTimer(LOGGER, "extract_solution"):
        # split the solution vector to get the face currents, the voxel potentials, and the sources
        n_offset = 0
        (I_fc, V_vc, n_offset) = extract_solution.get_sol_extract_field(sol, idx_fc, idx_vc, n_offset)
        (I_src_c, I_src_v, n_offset) = extract_solution.get_sol_extract_source(sol, idx_src_c, idx_src_v, n_offset)
        (I_fm, V_vm, n_offset) = extract_solution.get_sol_extract_field(sol, idx_fm, idx_vm, n_offset)

        # get the losses and energy
        (P_fc, P_fm) = extract_solution.get_losses(freq, I_fc, I_fm, R_c, R_m)
        (W_fc, W_fm) = extract_solution.get_energy(freq, I_fc, I_fm, L_op_c, K_op_c)

        # get the voxel flow densities from the face flows
        J_vc = extract_solution.get_vector_density(n, d, idx_fc, A_net_c, I_fc)
        B_vm = extract_solution.get_vector_density(n, d, idx_fm, A_net_m, I_fm)

        # get the voxel loss densities from the face losses
        P_vc = extract_solution.get_scalar_density(d, A_net_c, P_fc)
        P_vm = extract_solution.get_scalar_density(d, A_net_m, P_fm)

        # get the divergence of the face flows
        S_vc = extract_solution.get_divergence_density(d, A_net_c, I_fc)
        Q_vm = extract_solution.get_divergence_density(d, A_net_m, I_fm)

        # get the domain losses for the different materials
        material = extract_solution.get_material(material_idx, idx_vc, idx_vm, A_net_c, A_net_m, P_fc, P_fm)

        # get the terminal voltages and currents for the sources
        source = extract_solution.get_source(freq, source_idx, idx_src_c, idx_src_v, idx_vc, V_vc, I_src_c, I_src_v)

        # get the global quantities (energy and losses)
        integral = extract_solution.get_integral(P_fc, P_fm, W_fc, W_fm)

    # assign the results (will be merged in the solver output)
    data_sweep = {
        "freq": freq,
        "has_converged": has_converged,
        "solver_status": solver_status,
        "condition_status": condition_status,
        "material": material,
        "source": source,
        "integral": integral,
        "res": res,
        "conv": conv,
        "V_vc": V_vc,
        "V_vm": V_vm,
        "J_vc": J_vc,
        "B_vm": B_vm,
        "P_vc": P_vc,
        "P_vm": P_vm,
        "S_vc": S_vc,
        "Q_vm": Q_vm,
    }

    return data_sweep, sol


def run(data_voxel, data_problem, data_tolerance):
    """
    Main script for solving a problem with the PEEC solver.
    Handle invalid data with exceptions.

    Parameters
    ----------
    data_voxel :  dict
        The dict describes the voxel structure.
        The voxel grid (number, size, and origin) is defined.
        Different domains (with the indices of the voxel) are defined.
        The connected components of the graph defined by the voxel structure are defined.
    data_problem: dict
        The frequency of the problem is defined.
        The electric and magnetic materials are defined.
        The current and voltage sources are defined.
    data_tolerance: dict
        The dict describes the numerical options.
        The tolerances for simplifying the Green functions are defined.
        The tolerances for the matrix condition numbers are defined.
        The options for the iterative solver are defined.

    Returns
    -------
    status : boolean
        True if the call is successful.
        False if the problems are encountered.
    data_solution: dict
        The dict describes the problem solution.
        The voxel structure is defined.
        The frequency of the problem is defined.
        The status of the solution (solver convergence and condition number) is described.
        The resistivity, potential, current density, and loss density of the different voxel are defined.
        The terminals quantities (voltage and current) of the sources are defined.
        The integral quantities (total losses and energy) of the problem are defined.
    ex : exception
        The encountered exception (if any).
        None if the termination is successful.
    """

    # run the solver
    try:
        # check the problem and tolerance data
        LOGGER.info("check the input data")
        check_data_problem.check_data_problem(data_problem)
        check_data_tolerance.check_data_tolerance(data_tolerance)

        # combine the problem and voxel data
        LOGGER.info("combine the input data")
        (data_solver, sweep_config, sweep_param) = check_data_solver.get_data_solver(data_voxel, data_problem, data_tolerance)

        # create the problem
        with timelogger.BlockTimer(LOGGER, "init"):
            (data_init, data_internal) = _run_solver_init(data_solver)

        # function for solving a single sweep
        def fct_compute(tag, param, init):
            with timelogger.BlockTimer(LOGGER, "run sweep: " + tag):
                (output, init) = _run_solver_sweep(data_solver, data_init, data_internal, param, init)
            return output, init

        # compute the different sweeps
        data_sweep = sweep_solver.get_run_sweep(sweep_config, sweep_param, fct_compute)

        # extract the solution
        data_solution = {
            "data_init": data_init,
            "data_sweep": data_sweep,
        }
    except (CheckError, RunError) as ex:
        timelogger.log_exception(LOGGER, ex)
        return False, None, ex

    # end message
    LOGGER.info("successful termination")

    return True, data_solution, None
