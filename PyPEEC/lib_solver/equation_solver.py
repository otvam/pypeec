"""
Module for checking the matrix condition number and solving a sparse equation system.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import scipy.linalg as lna
from PyPEEC.lib_matrix import matrix_condition
from PyPEEC.lib_matrix import matrix_gmres
from PyPEEC.lib_utils import timelogger

# get a logger
logger = timelogger.get_logger("EQUATION")


def get_solver(sys_op, pcd_op, rhs, solver_options):
    """
    Solve a sparse equation system with gmres.
    The equation system and the preconditioner are described with linear operator.
    """

    # check preconditioner
    if pcd_op is None:
        logger.warning("matrix solver: preconditioner is not available")

    # call the solver
    (status, n_iter, res_iter, sol) = matrix_gmres.get_matrix_gmres(sys_op, pcd_op, rhs, solver_options)

    # compute the absolute and relative residuum
    res_raw = sys_op(sol)-rhs
    res_abs = lna.norm(res_raw)
    rhs_abs = lna.norm(rhs)
    if rhs_abs > 0:
        res_rel = res_abs/rhs_abs
    else:
        res_rel = float("nan")

    # get problem size
    n_dof = len(rhs)

    # assign the results
    solver_status = {
        "res_raw": res_raw,
        "res_abs": res_abs,
        "res_rel": res_rel,
        "n_iter": n_iter,
        "res_iter": res_iter,
        "n_dof": n_dof,
        "status": status,
    }

    # display status
    logger.info("matrix solver: n_dof = %d" % n_dof)
    logger.info("matrix solver: n_iter = %d" % n_iter)
    logger.info("matrix solver: res_abs = %.3e" % res_abs)
    logger.info("matrix solver: res_rel = %.3e" % res_rel)
    logger.info("matrix solver: status = %s" % status)
    if status:
        logger.info("matrix solver: convergence achieved")
    else:
        logger.warning("matrix solver: convergence issues")

    return sol, status, solver_status


def get_condition(S_mat, conditions_options):
    """
    Compute an estimate of the condition number (norm 1) of a sparse matrix.
    """

    # get the condition options
    check = conditions_options["check"]
    tolerance = conditions_options["tolerance"]
    norm_options = conditions_options["norm_options"]

    # computation is required
    if check:
        value = matrix_condition.get_condition_matrix(S_mat, norm_options)
    else:
        value = float(0)

    # check the condition
    status = value < tolerance

    # assign the results
    condition_status = {
        "check": check,
        "value": value,
        "status": status,
    }

    # display status
    logger.info("matrix condition: check = %s" % check)
    logger.info("matrix condition: value = %.3e" % value)
    logger.info("matrix condition: status = %s" % status)
    if status:
        logger.info("matrix condition: matrix condition is good")
    else:
        logger.warning("matrix condition: matrix condition is problematic")

    return status, condition_status
