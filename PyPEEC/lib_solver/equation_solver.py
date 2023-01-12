"""
Module for checking the matrix condition number and solving a sparse equation system.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import scipy.sparse.linalg as sla
import scipy.linalg as lna
from PyPEEC.lib_shared import logging_utils

# get a logger
logger = logging_utils.get_logger("equation")


class IterCounter:
    """
    Simple class used as a callback to count the number of iteration of the matrix solver.
    """

    def __init__(self):
        """
        Constructor.
        Init the number of iteration.
        """

        self.n_iter = 0
        self.res_vec = []
        self.iter_vec = []

    def get_callback(self, res):
        """
        Callback increasing the iteration count.
        """

        # update and save the iteration data
        self.n_iter += 1
        self.iter_vec.append(self.n_iter)
        self.res_vec.append(res)

        # log the results
        logger.info("matrix iter: i_iter = %d / res = %.3e" % (self.n_iter, res))

    def get_n_iter(self):
        """
        Get the number of iterations.
        """

        return self.n_iter, self.iter_vec, self.res_vec


def _get_lu_decomposition(mat):
    """
    Get an inverse operator (with LU decomposition) for the provided matrix and the Hermitian matrix.
    """

    # compute the LU decomposition
    try:
        LU_decomposition = sla.splu(mat)
    except RuntimeError:
        return None

    # get the function for the linear operator (original matrix)
    def fct_matvec(v):
        return LU_decomposition.solve(v, trans="N")

    # get the function for the linear operator (transposed matrix)
    def fct_rmatvec(v):
        return LU_decomposition.solve(v, trans="H")

    # assign linear operator for inversion
    op = sla.LinearOperator(mat.shape, matvec=fct_matvec, rmatvec=fct_rmatvec)

    return op


def _get_condition_estimate(mat, accuracy):
    """
    Compute an estimate of the condition number (norm 1) of a sparse matrix.
    """

    # get an inverse operator
    op = _get_lu_decomposition(mat)

    # abort if LU decomposition failed
    if op is None:
        return float("inf")

    # compute the norm of the matrix inverse (estimate)
    nrm_inv = sla.onenormest(op, t=accuracy)

    # compute the norm of the matrix (estimate)
    nrm_ori = sla.onenormest(mat, t=accuracy)

    # compute an estimate of the condition
    cond = nrm_ori*nrm_inv

    return cond


def get_solver(sys_op, pcd_op, rhs, solver_options):
    """
    Solve a sparse equation system with gmres.
    The equation system and the preconditioner are described with linear operator.
    """

    # get the solver options
    tol = solver_options["tol"]
    atol = solver_options["atol"]
    restart = solver_options["restart"]
    maxiter = solver_options["maxiter"]

    # object for counting the solver iterations (callback)
    obj = IterCounter()

    # define callback
    def fct(res_iter):
        obj.get_callback(res_iter)

    # call the solver
    (sol, flag) = sla.gmres(
        sys_op, rhs,
        tol=tol, atol=atol, restart=restart, maxiter=maxiter,
        M=pcd_op, callback=fct, callback_type="pr_norm",
    )

    # get the number of iterations
    (n_iter, iter_vec, res_vec) = obj.get_n_iter()

    # compute the absolute and relative residuum
    res = sys_op(sol)-rhs
    res_abs = lna.norm(res)
    rhs_abs = lna.norm(rhs)
    if rhs_abs > 0:
        res_rel = res_abs/rhs_abs
    else:
        res_rel = float("nan")

    # get problem size
    n_dof = len(rhs)

    # check for convergence
    status = flag == 0

    # assign the results
    solver_status = {
        "n_iter": n_iter,
        "iter_vec": iter_vec,
        "res_vec": res_vec,
        "res_abs": res_abs,
        "res_rel": res_rel,
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


def get_condition(mat, conditions_options):
    """
    Compute an estimate of the condition number (norm 1) of a sparse matrix.
    """

    # get the condition options
    check = conditions_options["check"]
    tolerance = conditions_options["tolerance"]
    accuracy = conditions_options["accuracy"]

    # computation is required
    if check:
        value = _get_condition_estimate(mat, accuracy)
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
