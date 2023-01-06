"""
Module for checking the matrix condition number and solving a sparse equation system.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import scipy.sparse.linalg as sla
import scipy.linalg as lna
from main import logging_utils

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


def get_solver(sys_op, pcd_op, rhs, cond, solver_options):
    """
    Solve a sparse equation system with gmres.
    The equation system and the preconditioner are described with linear operator.
    """

    # get the solver options
    tol = solver_options["tol"]
    atol = solver_options["atol"]
    restart = solver_options["restart"]
    maxiter = solver_options["maxiter"]
    condmax = solver_options["condmax"]

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
    res_rel = lna.norm(res)/lna.norm(rhs)

    # get problem size
    n_dof = len(rhs)

    # check for convergence
    cond_ok = cond < condmax
    solver_ok = flag == 0
    has_converged = cond_ok and solver_ok

    # assign the results
    solver_status = {
        "n_iter": n_iter,
        "iter_vec": iter_vec,
        "res_vec": res_vec,
        "res_abs": res_abs,
        "res_rel": res_rel,
        "cond": cond,
        "n_dof": n_dof,
        "cond_ok": cond_ok,
        "solver_ok": solver_ok,
    }

    # display status
    logger.info("matrix solver: n_dof = %d" % n_dof)
    logger.info("matrix solver: n_iter = %d" % n_iter)
    logger.info("matrix solver: cond = %.3e" % cond)
    logger.info("matrix solver: res_abs = %.3e" % res_abs)
    logger.info("matrix solver: res_rel = %.3e" % res_rel)
    logger.info("matrix solver: cond_ok = %s" % cond_ok)
    logger.info("matrix solver: solver_ok = %s" % solver_ok)
    if has_converged:
        logger.info("matrix solver: convergence achieved")
    else:
        logger.warning("matrix solver: convergence issues")

    return sol, has_converged, solver_status


def get_condition(mat):
    """
    Compute an estimate of the condition number (norm 1) of a sparse matrix.
    """

    # compute the LU decomposition
    try:
        LU_decomposition = sla.splu(mat)
    except RuntimeError:
        return float('inf')

    # get the function for the linear operator (original matrix)
    def fct_matvec(v):
        return LU_decomposition.solve(v, trans="N")

    # get the function for the linear operator (transposed matrix)
    def fct_rmatvec(v):
        return LU_decomposition.solve(v, trans="H")

    # assign linear operator for inversion
    op = sla.LinearOperator(mat.shape, matvec=fct_matvec, rmatvec=fct_rmatvec)

    # compute the norm of the matrix inverse (estimate)
    nrm_inv = sla.onenormest(op)

    # compute the norm of the matrix (estimate)
    nrm_ori = sla.onenormest(mat)

    # compute an estimate of the condition
    cond = nrm_ori*nrm_inv

    return cond
