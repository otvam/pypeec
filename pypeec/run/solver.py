"""
Main script for solving a problem with the PEEC solver.
Check the input data, solve the problem, and parse the results.
The different parts of the code are timed.

The solver is implemented with NumPy and Scipy.
Optional HPC libraries can be used to accelerate the solver.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import copy
import scilogger
from pypeec.lib_matrix import matrix_factorization
from pypeec.lib_matrix import multiply_fft
from pypeec.lib_matrix import fourier_transform
from pypeec.lib_solver import sweep_joblib
from pypeec.lib_solver import voxel_geometry
from pypeec.lib_solver import system_tensor
from pypeec.lib_solver import problem_geometry
from pypeec.lib_solver import problem_value
from pypeec.lib_solver import system_matrix
from pypeec.lib_solver import equation_system
from pypeec.lib_solver import equation_solver
from pypeec.lib_solver import extract_solution
from pypeec.lib_solver import extract_convergence
from pypeec.lib_check import check_data_format
from pypeec.lib_check import check_data_options


# get a logger
LOGGER = scilogger.get_logger(__name__, "pypeec")


def _run_solver_options(data_solver):
    """
    Load and configure the optional libraries.
    """

    # extract the data
    factorization_options = data_solver["factorization_options"]
    fft_options = data_solver["fft_options"]

    # set options
    matrix_factorization.set_options(factorization_options)
    fourier_transform.set_options(fft_options)
    multiply_fft.set_options(fft_options)


def _run_solver_init(data_solver):
    """
    Compute the voxel geometry, Green functions, and the incidence matrix.
    """

    # extract the data
    n = data_solver["n"]
    d = data_solver["d"]
    c = data_solver["c"]
    parallel_sweep = data_solver["parallel_sweep"]
    integral_simplify = data_solver["integral_simplify"]
    mult_type = data_solver["mult_type"]
    source_def = data_solver["source_def"]
    material_def = data_solver["material_def"]
    domain_def = data_solver["domain_def"]
    graph_def = data_solver["graph_def"]
    pts_cloud = data_solver["pts_cloud"]
    sweep_solver = data_solver["sweep_solver"]

    # load and configure the optional libraries
    _run_solver_options(data_solver)

    # get the voxel geometry and the incidence matrix
    with LOGGER.BlockTimer("voxel_geometry"):
        # get the coordinate of the voxels
        pts_vox = voxel_geometry.get_voxel_coordinate(n, d, c)

        # compute the incidence matrix
        A_vox = voxel_geometry.get_incidence_matrix(n)

    # parse the problem geometry (materials and sources)
    with LOGGER.BlockTimer("problem_geometry"):
        # get indices
        (idx_vc, idx_vm, material_idx) = problem_geometry.get_material_idx(material_def, domain_def)
        (idx_src_c, idx_src_v, source_idx) = problem_geometry.get_source_idx(source_def, domain_def)

        # convert the indices
        material_idx = problem_geometry.get_material_pos(material_idx, idx_vc, idx_vm)
        source_idx = problem_geometry.get_source_pos(source_idx, idx_vc, idx_src_c, idx_src_v)

        # check problem type
        has_magnetic = problem_geometry.get_problem_type(idx_vc, idx_vm, idx_src_c, idx_src_v, graph_def)

        # reduce the incidence matrix to the non-empty voxels and compute face indices
        (pts_net_c, A_net_c, idx_fc) = problem_geometry.get_reduce_matrix(pts_vox, A_vox, idx_vc)
        (pts_net_m, A_net_m, idx_fm) = problem_geometry.get_reduce_matrix(pts_vox, A_vox, idx_vm)

        # free memory
        del pts_vox
        del A_vox

        # get a summary of the problem size
        problem_status = problem_geometry.get_status(n, idx_vc, idx_vm, idx_fc, idx_fm, idx_src_c, idx_src_v)

    # get the Green functions
    with LOGGER.BlockTimer("system_tensor"):
        # Green function self-coefficient
        G_self = system_tensor.get_green_self(d)

        # Green function mutual coefficients
        G_mutual = system_tensor.get_green_tensor(n, d, integral_simplify)

        # Green function mutual coefficients
        K_tsr = system_tensor.get_coupling_tensor(n, d, integral_simplify, has_magnetic)

    # get the system operators
    with LOGGER.BlockTimer("system_matrix"):
        # get the inductance tensor (preconditioner and full problem)
        (L_c, L_op_c) = system_matrix.get_inductance_matrix(n, d, idx_fc, G_self, G_mutual, mult_type)

        # get the potential tensor (preconditioner and full problem)
        (P_m, P_op_m) = system_matrix.get_potential_matrix(d, idx_vm, G_self, G_mutual, mult_type)

        # free memory
        del G_self
        del G_mutual

        # get the coupling matrices
        (K_op_c, K_op_m) = system_matrix.get_coupling_matrix(n, idx_vc, idx_vm, idx_fc, idx_fm, A_net_c, A_net_m, K_tsr, mult_type)

        # free memory
        del K_tsr

    # assign the results (internal data required to solve the problem)
    data_internal = {
        "idx_vc": idx_vc,
        "idx_vm": idx_vm,
        "idx_fc": idx_fc,
        "idx_fm": idx_fm,
        "idx_src_c": idx_src_c,
        "idx_src_v": idx_src_v,
        "A_net_c": A_net_c,
        "A_net_m": A_net_m,
        "L_c": L_c,
        "L_op_c": L_op_c,
        "P_m": P_m,
        "P_op_m": P_op_m,
        "K_op_c": K_op_c,
        "K_op_m": K_op_m,
        "material_idx": material_idx,
        "source_idx": source_idx,
        "pts_net_c": pts_net_c,
        "pts_net_m": pts_net_m,
    }

    # assign the results (will be merged in the solver output)
    data_init = {
        "n": n,
        "d": d,
        "c": c,
        "problem_status": problem_status,
        "idx_vc": idx_vc,
        "idx_vm": idx_vm,
        "idx_fc": idx_fc,
        "idx_fm": idx_fm,
        "idx_src_c": idx_src_c,
        "idx_src_v": idx_src_v,
        "pts_cloud": pts_cloud,
        "pts_net_c": pts_net_c,
        "pts_net_m": pts_net_m,
    }

    return data_init, data_internal, sweep_solver, parallel_sweep


def _run_solver_sweep(data_solver, data_internal, data_param, sol_init):
    """
    Create the equation system, solve the system, and extract the solution.
    """

    # extract the data
    n = data_solver["n"]
    d = data_solver["d"]
    biot_savart = data_solver["biot_savart"]
    condition_options = data_solver["condition_options"]
    solver_options = data_solver["solver_options"]
    pts_cloud = data_solver["pts_cloud"]

    # extract the data
    idx_vc = data_internal["idx_vc"]
    idx_vm = data_internal["idx_vm"]
    idx_fc = data_internal["idx_fc"]
    idx_fm = data_internal["idx_fm"]
    idx_src_c = data_internal["idx_src_c"]
    idx_src_v = data_internal["idx_src_v"]
    A_net_c = data_internal["A_net_c"]
    A_net_m = data_internal["A_net_m"]
    L_c = data_internal["L_c"]
    L_op_c = data_internal["L_op_c"]
    P_m = data_internal["P_m"]
    P_op_m = data_internal["P_op_m"]
    K_op_c = data_internal["K_op_c"]
    K_op_m = data_internal["K_op_m"]
    material_idx = data_internal["material_idx"]
    source_idx = data_internal["source_idx"]
    pts_net_c = data_internal["pts_net_c"]
    pts_net_m = data_internal["pts_net_m"]

    # extract the data
    freq = data_param["freq"]
    material_val = data_param["material_val"]
    source_val = data_param["source_val"]

    # load and configure the optional libraries
    _run_solver_options(data_solver)

    # get the material and source values
    with LOGGER.BlockTimer("problem_value"):
        # complete value
        material_all = problem_value.get_material_value(material_val, material_idx)
        source_all = problem_value.get_source_value(source_val, source_idx)

        # parse the material parameters
        (rho_vc, rho_vm) = problem_value.get_material_vector(material_all)

        # parse the source parameters
        (I_src_c, Y_src_c) = problem_value.get_source_vector(source_all, "current")
        (V_src_v, Z_src_v) = problem_value.get_source_vector(source_all, "voltage")

        # get the resistance vector
        R_c = problem_value.get_resistance_vector(n, d, A_net_c, idx_fc, rho_vc)
        R_m = problem_value.get_resistance_vector(n, d, A_net_m, idx_fm, rho_vm)

    # assemble the equation system
    with LOGGER.BlockTimer("equation_system"):
        # compute the right-hand vector with the sources
        rhs = equation_system.get_source_vector(idx_vc, idx_vm, idx_fc, idx_fm, I_src_c, V_src_v)

        # get the source connection matrices
        A_src = equation_system.get_source_matrix(idx_vc, idx_src_c, idx_src_v, Y_src_c, Z_src_v)

        # get the linear operator for the preconditioner (guess of the inverse)
        (fct_pcd, S_mat) = equation_system.get_cond_operator(freq, A_net_c, A_net_m, A_src, R_c, R_m, L_c, P_m)

        # get the linear operator for the electric-magnetic coupling
        fct_cpl = equation_system.get_coupling_operator(freq, A_net_c, A_net_m, A_src, K_op_c, K_op_m)

        # get the linear operator for the full system (matrix-vector multiplication)
        fct_sys = equation_system.get_system_operator(freq, A_net_c, A_net_m, A_src, R_c, R_m, L_op_c, P_op_m)

        # get the source indices
        sol_idx = equation_system.get_system_sol_idx(A_net_c, A_net_m, A_src)

    # solve the equation system
    with LOGGER.BlockTimer("equation_solver"):
        # estimate the condition number of the problem (to detect quasi-singular problem)
        (condition_ok, condition_status) = equation_solver.get_condition(S_mat, condition_options)

        # free memory
        del S_mat

        # get a function to evaluate the solver convergence
        fct_conv = extract_convergence.get_fct_conv(freq, source_all, sol_idx)

        # solve the equation system
        (sol, res, conv, solver_ok, solver_status) = equation_solver.get_solver(sol_init, fct_cpl, fct_sys, fct_pcd, rhs, fct_conv, solver_options)

        # free memory
        del fct_pcd
        del fct_cpl
        del fct_sys
        del fct_conv

        # compute convergence
        has_converged = solver_ok and condition_ok

    # extract the solution
    with LOGGER.BlockTimer("extract_solution"):
        # split the solution vector to get the face currents, the voxel potentials, and the sources
        (I_fc, V_vc, I_fm, V_vm, I_src) = extract_solution.get_sol_extract(sol, sol_idx)

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
        material = extract_solution.get_material(material_all, A_net_c, A_net_m, P_fc, P_fm)

        # get the terminal voltages and currents for the sources
        (source, S_total) = extract_solution.get_source(freq, source_all, I_src, V_vc)

        # get the global quantities (energy and losses)
        integral = extract_solution.get_integral(P_fc, P_fm, W_fc, W_fm, S_total)

        # get the cloud point magnetic field (contributions of the electric domains)
        H_pts_c = extract_solution.get_magnetic_field_electric(n, d, idx_fc, A_net_c, I_fc, pts_net_c, pts_cloud, biot_savart)

        # get the cloud point magnetic field (contributions of the magnetic domains)
        H_pts_m = extract_solution.get_magnetic_field_magnetic(A_net_m, I_fm, pts_net_m, pts_cloud)

    # assemble solution
    var = {
        "V_c": {"var": V_vc, "cat": "scalar_electric"},
        "P_c": {"var": P_vc, "cat": "scalar_electric"},
        "S_c": {"var": S_vc, "cat": "scalar_electric"},
        "J_c": {"var": J_vc, "cat": "vector_electric"},
        "V_m": {"var": V_vm, "cat": "scalar_magnetic"},
        "P_m": {"var": P_vm, "cat": "scalar_magnetic"},
        "Q_m": {"var": Q_vm, "cat": "scalar_magnetic"},
        "B_m": {"var": B_vm, "cat": "vector_magnetic"},
        "H_p": {"var": H_pts_c + H_pts_m, "cat": "cloud"},
    }

    # assign the results (will be merged in the solver output)
    data_sweep = {
        "freq": freq,
        "has_converged": has_converged,
        "solver_ok": solver_ok,
        "condition_ok": condition_ok,
        "solver_status": solver_status,
        "condition_status": condition_status,
        "material": material,
        "source": source,
        "integral": integral,
        "conv": conv,
        "res": res,
        "var": var,
    }

    return data_sweep, sol


def _run_parallel_sweep(tag, sol_init, data_solver, data_internal, data_param):
    """
    Wrapper to solve a sweep in parallel (ensure that everything can be serialized).
    """

    with LOGGER.BlockTimer("run sweep: " + tag):
        (data_sweep, sol) = _run_solver_sweep(data_solver, data_internal, data_param, sol_init)

    return data_sweep, sol


def _get_data(data_init, data_sweep, timestamp):
    """
    Assemble the returned data.
    """

    # end message
    (seconds, duration, date) = scilogger.get_duration(timestamp)

    # get status
    status = True
    for data_sweep_tmp in data_sweep.values():
        status = status and data_sweep_tmp["has_converged"]
        status = status and data_sweep_tmp["solver_ok"]
        status = status and data_sweep_tmp["condition_ok"]

    # get warning
    if not status:
        LOGGER.warning("problem detected for the solver")

    # extract the solution
    data_solution = {
        "date": date,
        "duration": duration,
        "seconds": seconds,
        "status": status,
        "data_init": data_init,
        "data_sweep": data_sweep,
    }

    return data_solution


def run(data_voxel, data_problem, data_tolerance):
    """
    Main script for solving a problem with the PEEC solver.
    Handle invalid data with exceptions.
    """

    # get timestamp
    timestamp = scilogger.get_timestamp()

    # make copies of inputs
    data_voxel = copy.deepcopy(data_voxel)
    data_problem = copy.deepcopy(data_problem)
    data_tolerance = copy.deepcopy(data_tolerance)

    # check the voxel data
    LOGGER.info("check the voxel data")
    (status, data_geom) = check_data_options.check_data_voxel(data_voxel)
    if not status:
        LOGGER.warning("invalid status for the voxel data")

    # check the input data
    LOGGER.info("check the input data")
    check_data_format.check_data_problem(data_problem)
    check_data_format.check_data_tolerance(data_tolerance)

    # combine the problem and voxel data
    LOGGER.info("combine the input data")
    data_solver = {**data_tolerance, **data_geom, **data_problem}

    # create the problem
    with LOGGER.BlockTimer("init"):
        (data_init, data_internal, sweep_solver, parallel_sweep) = _run_solver_init(data_solver)

    # function for solving a single sweep
    def fct_compute(tag, data_param, sol_init):
        return _run_parallel_sweep(tag, sol_init, data_solver, data_internal, data_param)

    # compute the different sweeps
    data_sweep = sweep_joblib.get_run_sweep(parallel_sweep, sweep_solver, fct_compute)

    # create output data
    data_solution = _get_data(data_init, data_sweep, timestamp)

    return data_solution
