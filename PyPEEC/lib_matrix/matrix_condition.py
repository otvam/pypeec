"""
Module for estimating the condition number of sparse matrices.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import scipy.sparse.linalg as sla
from PyPEEC.lib_utils import timelogger

# get a logger
logger = timelogger.get_logger("CONDITION")


def _get_decomposition(mat):
    """
    Get the LU decomposition of the provided matrix.
    """

    try:
        decomposition = sla.splu(mat)
    except RuntimeError:
        decomposition = None

    return decomposition


def _get_inverse_operator(mat, decomposition):
    """
    Get an inverse operator (with LU decomposition) for the provided matrix and the Hermitian matrix.
    """

    # get the function for the linear operator (original matrix)
    def fct_matvec(v):
        return decomposition.solve(v, trans="N")

    # get the function for the linear operator (transposed matrix)
    def fct_rmatvec(v):
        return decomposition.solve(v, trans="H")

    # assign linear operator for inversion
    op = sla.LinearOperator(mat.shape, matvec=fct_matvec, rmatvec=fct_rmatvec)

    return op


def get_condition_matrix(mat, norm_options):
    """
    Compute an estimate of the condition number (norm 1) of a sparse matrix.
    """

    # get the options
    t_accuracy = norm_options["t_accuracy"]
    n_iter_max = norm_options["n_iter_max"]

    # get LU decomposition
    logger.info("compute LU decomposition")
    decomposition = _get_decomposition(mat)

    # abort if LU decomposition failed
    if decomposition is None:
        logger.info("condition estimate is infinite")
        return float("inf")

    # get the inverse operator
    op = _get_inverse_operator(mat, decomposition)

    # compute the norm of the matrix inverse (estimate)
    logger.info("compute estimate norm of the inverse")
    nrm_inv = sla.onenormest(op, t=t_accuracy, itmax=n_iter_max)

    # compute the norm of the matrix (estimate)
    logger.info("compute estimate norm of the matrix")
    nrm_ori = sla.onenormest(mat, t=t_accuracy, itmax=n_iter_max)

    # compute an estimate of the condition
    logger.info("compute condition estimate")
    cond = nrm_ori*nrm_inv

    return cond
