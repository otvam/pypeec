"""
Module for solving a sparse equation system with GMRES.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import scipy.sparse.linalg as sla
from pypeec.lib_utils import timelogger

# get a logger
logger = timelogger.get_logger("GMRES")


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

    # init list for storing the residuum (callback)
    logger.debug("enter matrix solver")

    # list for storing the residuum
    conv = []

    # define callback
    def fct(res):
        conv.append(res)
        logger.debug("matrix iter: iter = %d / res = %.3e" % (len(conv), res))

    # call the solver
    (sol, flag) = sla.gmres(
        sys_op, rhs,
        tol=rel_tol, atol=abs_tol,
        restart=n_between_restart, maxiter=n_maximum_restart,
        M=pcd_op, callback=fct, callback_type="pr_norm",
    )

    # check for convergence
    status = flag == 0

    # exit
    logger.debug("exit matrix solver")

    return status, conv, sol
