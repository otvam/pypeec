"""
Module for solving a sparse equation system with GMRES.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import scipy.sparse.linalg as sla
from pypeec.lib_utils import timelogger

# get a logger
logger = timelogger.get_logger("GMRES")


class _IterCounter:
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
        logger.debug("matrix iter: i_iter = %d / res = %.3e" % (self.n_iter, res))

    def get_n_iter(self):
        """
        Get the number of iterations.
        """

        return self.n_iter, self.res_iter


def get_matrix_gmres(sys_op, pcd_op, rhs, gmres_options):
    """
    Solve a sparse equation system with GMRES.
    The equation system and the preconditioner are described with linear operator.
    """

    # get the options
    rel_tol = gmres_options["rel_tol"]
    abs_tol = gmres_options["abs_tol"]
    n_between_restart = gmres_options["n_between_restart"]
    n_maximum_restart = gmres_options["n_maximum_restart"]

    # object for counting the solver iterations (callback)
    obj = _IterCounter()

    # define callback
    def fct(res):
        obj.get_callback(res)

    # call the solver
    logger.debug("start matrix solver")
    (sol, flag) = sla.gmres(
        sys_op, rhs,
        tol=rel_tol, atol=abs_tol,
        restart=n_between_restart, maxiter=n_maximum_restart,
        M=pcd_op, callback=fct, callback_type="pr_norm",
    )
    logger.debug("exit matrix solver")

    # get the number of iterations
    (n_iter, res_iter) = obj.get_n_iter()

    # check for convergence
    status = flag == 0

    return status, n_iter, res_iter, sol
