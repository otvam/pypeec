"""
Module for solving a sparse equation system with GMRES.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import scipy.sparse.linalg as sla
from pypeec import log

# get a logger
LOGGER = log.get_logger("GMRES")


class _IterCounter:
    """
    Simple class used as a callback to count the number of iteration of the matrix solver.
    """

    def __init__(self, fct_conv):
        """
        Constructor.
        Init the number of iteration.
        """

        self.fct_conv = fct_conv
        self.n_iter = 0
        self.P_vec = []
        self.Q_vec = []

    def get_callback(self, x):
        """
        Callback increasing the iteration count.
        """

        # get the power
        (P_tot, Q_tot) = self.fct_conv(x)

        # update the iteration
        self.n_iter += 1

        # save the data
        self.P_vec.append(P_tot)
        self.Q_vec.append(Q_tot)

        # log the results
        LOGGER.debug("matrix iter: iter = %d / P_tot = %.3e / Q_tot = %.3e" % (self.n_iter, P_tot, Q_tot))

    def get_n_iter(self):
        """
        Get the number of iterations.
        """

        return self.n_iter

    def get_conv(self):
        """
        Get the number of iterations.
        """

        conv = {"P_vec": self.P_vec, "Q_vec": self.Q_vec}

        return conv


def get_matrix_gmres(sol_init, sys_op, pcd_op, rhs, fct_conv, gmres_options):
    """
    Solve a sparse equation system with GMRES.
    The equation system and the preconditioner are described with linear operator.
    """

    # get the options
    rel_tol = gmres_options["rel_tol"]
    abs_tol = gmres_options["abs_tol"]
    n_between_restart = gmres_options["n_between_restart"]
    n_maximum_restart = gmres_options["n_maximum_restart"]

    # init list for storing the residuum (callback)
    LOGGER.debug("enter matrix solver")

    # object for counting the solver iterations (callback)
    obj = _IterCounter(fct_conv)

    # define callback
    def fct(x):
        obj.get_callback(x)

    # call the solver
    (sol, flag) = sla.gmres(
        sys_op, rhs,
        x0=sol_init, tol=rel_tol, atol=abs_tol,
        restart=n_between_restart, maxiter=n_maximum_restart,
        M=pcd_op, callback=fct, callback_type="x",
    )

    # get the number of iterations
    n_iter = obj.get_n_iter()
    conv = obj.get_conv()

    # check for convergence
    status = flag == 0

    # exit
    LOGGER.debug("exit matrix solver")

    return status, n_iter, conv, sol
