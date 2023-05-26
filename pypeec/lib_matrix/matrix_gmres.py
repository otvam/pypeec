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

    def __init__(self, fct_conv, callback_type):
        """
        Constructor.
        Init the number of iteration.
        """

        # assign data
        self.fct_conv = fct_conv
        self.callback_type = callback_type

        # init data
        self.n_iter = 0
        self.iter_vec = []
        self.P_vec = []
        self.Q_vec = []
        self.res_vec = []

    def get_callback_tag(self):
        if self.callback_type == "sol":
            callback_tag = "x"
        elif self.callback_type == "res":
            callback_tag = "pr_norm"
        else:
            raise ValueError("invalid callback type")

        return callback_tag

    def get_callback_run(self, data):
        """
        Callback increasing the iteration count.
        """

        # update the iteration
        self.n_iter += 1
        self.iter_vec.append(self.n_iter)

        # run the callback
        if self.callback_type == "sol":
            # get the power
            (P_tot, Q_tot) = self.fct_conv(data)

            # save the data
            self.P_vec.append(P_tot)
            self.Q_vec.append(Q_tot)

            # log the results
            LOGGER.debug("matrix iter: iter = %d / P_tot = %.3e / Q_tot = %.3e" % (self.n_iter, P_tot, Q_tot))
        elif self.callback_type == "res":
            # save the data
            self.res_vec.append(data)

            # log the results
            LOGGER.debug("matrix iter: iter = %d / res = %.3e" % (self.n_iter, data))
        else:
            raise ValueError("invalid callback type")

    def get_n_iter(self):
        """
        Get the number of iterations.
        """

        return self.n_iter

    def get_conv(self):
        """
        Get the number of iterations.
        """

        if self.callback_type == "sol":
            conv = {
                "callback_type": self.callback_type,
                "iter_vec": self.iter_vec,
                "P_vec": self.P_vec,
                "Q_vec": self.Q_vec
            }
        elif self.callback_type == "res":
            conv = {
                "callback_type": self.callback_type,
                "iter_vec": self.iter_vec,
                "res_vec": self.res_vec,
            }
        else:
            raise ValueError("invalid callback type")

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
    callback_type = gmres_options["callback_type"]

    # init list for storing the residuum (callback)
    LOGGER.debug("enter matrix solver")

    # object for counting the solver iterations (callback)
    obj = _IterCounter(fct_conv, callback_type)

    # get callback tag
    callback_tag = obj.get_callback_tag()

    # define callback
    def fct_callback(data):
        obj.get_callback_run(data)

    # call the solver
    (sol, flag) = sla.gmres(
        sys_op, rhs,
        x0=sol_init, tol=rel_tol, atol=abs_tol,
        restart=n_between_restart, maxiter=n_maximum_restart,
        M=pcd_op, callback=fct_callback, callback_type=callback_tag,
    )

    # get the number of iterations
    n_iter = obj.get_n_iter()
    conv = obj.get_conv()

    # check for convergence
    status = flag == 0

    # exit
    LOGGER.debug("exit matrix solver")

    return status, n_iter, conv, sol
