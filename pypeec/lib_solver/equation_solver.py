"""
Module for checking the matrix condition number and solving a sparse equation system.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import scipy.linalg as lna
from pypeec.lib_matrix import matrix_condition
from pypeec.lib_matrix import matrix_gmres
from pypeec.lib_utils import timelogger

# get a logger
LOGGER = timelogger.get_logger("EQUATION")


def get_solver(sys_op, pcd_op, rhs, solver_options):
    """
    Solve a sparse equation system with gmres.
    The equation system and the preconditioner are described with linear operator.
    """

    # get the condition options
    tolerance = solver_options["tolerance"]
    gmres_options = solver_options["gmres_options"]

    # get problem size
    n_dof = len(rhs)

    # check preconditioner
    status_pcd = pcd_op is not None

    # call the solver
    (status_gmres, conv, sol) = matrix_gmres.get_matrix_gmres(sys_op, pcd_op, rhs, gmres_options)

    # compute and check the residuum
    res = sys_op(sol)-rhs
    res_norm = lna.norm(res)
    status_res = res_norm < tolerance
    n_iter = len(conv)

    # assign the results
    solver_status = {
        "res_norm": res_norm,
        "n_iter": n_iter,
        "n_dof": n_dof,
        "status_gmres": status_gmres,
        "status_res": status_res,
    }

    # solver success
    status = status_gmres and status_res and status_pcd

    # display status
    LOGGER.debug("matrix solver: n_dof = %d" % n_dof)
    LOGGER.debug("matrix solver: n_iter = %d" % n_iter)
    LOGGER.debug("matrix solver: res_norm = %.3e" % res_norm)
    LOGGER.debug("matrix solver: status_pcd = %s" % status_pcd)
    LOGGER.debug("matrix solver: status_gmres = %s" % status_gmres)
    LOGGER.debug("matrix solver: status_res = %s" % status_res)
    if pcd_op is None:
        LOGGER.warning("matrix solver: preconditioner issue")
    if status_gmres is None:
        LOGGER.warning("matrix solver: gmres issue")
    if status_res is None:
        LOGGER.warning("matrix solver: residuum issue")
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
