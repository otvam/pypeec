"""
Module for solving a sparse equation system with GMRES.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import scipy.sparse.linalg as sla
from pypeec import utils_log

# get a logger
LOGGER = utils_log.get_logger("GMRES")


def get_matrix_gmres(sol_init, sys_op, pcd_op, rhs, gmres_options):
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

    # list for storing the residuum
    conv = []

    # define callback
    def fct(res):
        conv.append(res)
        LOGGER.debug("matrix iter: iter = %d / res = %.3e" % (len(conv), res))

    # call the solver
    (sol, flag) = sla.gmres(
        sys_op, rhs,
        x0=sol_init, tol=rel_tol, atol=abs_tol,
        restart=n_between_restart, maxiter=n_maximum_restart,
        M=pcd_op, callback=fct, callback_type="pr_norm",
    )

    # check for convergence
    status = flag == 0

    # exit
    LOGGER.debug("exit matrix solver")

    return status, conv, sol
