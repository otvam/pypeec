"""
Module for estimating the condition number of sparse matrices.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import scipy.sparse.linalg as sla
from PyPEEC.lib_utils import timelogger

# get a logger
logger = timelogger.get_logger("CONDITION")


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


def get_condition_matrix(mat, accuracy):
    """
    Compute an estimate of the condition number (norm 1) of a sparse matrix.
    """

    # get an inverse operator
    logger.info("compute LU decomposition")
    op = _get_lu_decomposition(mat)

    # abort if LU decomposition failed
    if op is None:
        return float("inf")

    # compute the norm of the matrix inverse (estimate)
    logger.info("compute estimate norm of the inverse")
    nrm_inv = sla.onenormest(op, t=accuracy)

    # compute the norm of the matrix (estimate)
    logger.info("compute estimate norm of the matrix")
    nrm_ori = sla.onenormest(mat, t=accuracy)

    # compute an estimate of the condition
    logger.info("compute condition estimate")
    cond = nrm_ori*nrm_inv

    return cond
