"""
Module for checking the matrix condition number and solving a sparse equation system.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import numpy as np
from pypeec.lib_matrix import matrix_condition
from pypeec.lib_matrix import matrix_iter
from pypeec import log

# get a logger
LOGGER = log.get_logger("EQUATION")


def get_solver(sol_init, sys_op, pcd_op, rhs, fct_conv, solver_options):
    """
    Solve a sparse equation system with gmres.
    The equation system and the preconditioner are described with linear operator.
    """

    # get the condition options
    check = solver_options["check"]
    tolerance = solver_options["tolerance"]
    iter_options = solver_options["iter_options"]

    # call the solver
    (status_solver, alg, sol) = matrix_iter.get_solve(sol_init, sys_op, pcd_op, rhs, fct_conv, iter_options)

    # compute and check the residuum
    res = sys_op(sol)-rhs
    res_rms = np.sqrt(np.mean(np.abs(res)**2))

    # get problem size
    n_dof = len(rhs)

    # get status
    status_pcd = pcd_op is not None
    status_res = res_rms < tolerance

    # extract alg results
    n_sys_eval = alg["n_sys_eval"]
    n_pcd_eval = alg["n_pcd_eval"]
    n_iter = alg["n_iter"]
    conv = alg["conv"]

    # assign the results
    solver_status = {
        "check": check,
        "n_dof": n_dof,
        "n_iter": n_iter,
        "n_sys_eval": n_sys_eval,
        "n_pcd_eval": n_pcd_eval,
        "res_rms": res_rms,
        "status_pcd": status_pcd,
        "status_solver": status_solver,
        "status_res": status_res,
    }

    # solver success
    if check:
        status = status_solver and status_res and status_pcd
    else:
        status = True

    # display results
    LOGGER.debug("matrix solver: n_dof = %d" % n_dof)
    LOGGER.debug("matrix solver: n_iter = %d" % n_iter)
    LOGGER.debug("matrix solver: n_sys_eval = %d" % n_sys_eval)
    LOGGER.debug("matrix solver: n_pcd_eval = %d" % n_pcd_eval)
    LOGGER.debug("matrix solver: res_rms = %.3e" % res_rms)
    LOGGER.debug("matrix solver: check = %s" % check)
    LOGGER.debug("matrix solver: status_pcd = %s" % status_pcd)
    LOGGER.debug("matrix solver: status_solver = %s" % status_solver)
    LOGGER.debug("matrix solver: status_res = %s" % status_res)

    # display warnings
    if not status_pcd:
        LOGGER.warning("matrix solver: preconditioner issue")
    if not status_solver:
        LOGGER.warning("matrix solver: iterative solver issue")
    if not status_res:
        LOGGER.warning("matrix solver: residuum issue")

    # display status
    if status:
        LOGGER.debug("matrix solver: convergence achieved")
    else:
        LOGGER.warning("matrix solver: convergence issues")

    return sol, res, conv, status, solver_status


def get_condition(S_mat_c, S_mat_m, conditions_options):
    """
    Compute an estimate of the condition number (norm 1) of preconditioner Schur complements.
    The condition number is used to detect problematic (quasi-singular) systems.
    """

    # get the condition options
    check = conditions_options["check"]
    tolerance = conditions_options["tolerance"]
    norm_options = conditions_options["norm_options"]

    # check the condition
    if check:
        value_electric = matrix_condition.get_condition_matrix("electric", S_mat_c, norm_options)
        value_magnetic = matrix_condition.get_condition_matrix("magnetic", S_mat_m, norm_options)
        status = (value_electric < tolerance) and (value_magnetic < tolerance)
    else:
        value_electric = float("nan")
        value_magnetic = float("nan")
        status = True

    # assign the results
    condition_status = {
        "check": check,
        "value_electric": value_electric,
        "value_magnetic": value_magnetic,
        "status": status,
    }

    # display status
    LOGGER.debug("matrix condition: check = %s" % check)
    LOGGER.debug("matrix condition: status = %s" % status)
    if check:
        LOGGER.debug("matrix condition: value_electric = %.3e" % value_electric)
        LOGGER.debug("matrix condition: value_magnetic = %.3e" % value_magnetic)
        if status:
            LOGGER.debug("matrix condition: matrix condition is good")
        else:
            LOGGER.warning("matrix condition: matrix condition is problematic")
    else:
        LOGGER.debug("matrix condition: matrix condition is not computed")

    return status, condition_status
