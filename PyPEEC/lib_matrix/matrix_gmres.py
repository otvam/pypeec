"""
Module for solving a sparse equation system with GMRES.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import scipy.sparse.linalg as sla
from PyPEEC.lib_utils import timelogger

# get a logger
logger = timelogger.get_logger("GMRES")


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
        self.res_iter = []

    def get_callback(self, res):
        """
        Callback increasing the iteration count.
        """

        # update and save the iteration data
        self.n_iter += 1
        self.res_iter.append(res)

        # log the results
        logger.info("matrix iter: i_iter = %d / res = %.3e" % (self.n_iter, res))

    def get_n_iter(self):
        """
        Get the number of iterations.
        """

        return self.n_iter, self.res_iter


def get_matrix_gmres(sys_op, pcd_op, rhs, tol, atol, restart, maxiter):
    """
    Solve a sparse equation system with gmres.
    The equation system and the preconditioner are described with linear operator.
    """

    # object for counting the solver iterations (callback)
    obj = IterCounter()

    # define callback
    def fct(res_tmp):
        obj.get_callback(res_tmp)

    # call the solver
    logger.info("start solver")
    (sol, flag) = sla.gmres(
        sys_op, rhs,
        tol=tol, atol=atol, restart=restart, maxiter=maxiter,
        M=pcd_op, callback=fct, callback_type="pr_norm",
    )
    logger.info("exit solver")

    # get the number of iterations
    (n_iter, res_iter) = obj.get_n_iter()

    # check for convergence
    status = flag == 0

    return status, n_iter, res_iter, sol