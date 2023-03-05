"""
Module for estimating the condition number of sparse matrices.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import scipy.sparse.linalg as sla
from pypeec.lib_utils import timelogger
from pypeec.lib_utils import config

# get config
NP_TYPES = config.NP_TYPES

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
        v = v.astype(NP_TYPES.COMPLEX)
        return decomposition.solve(v, trans="N")

    # get the function for the linear operator (transposed matrix)
    def fct_rmatvec(v):
        v = v.astype(NP_TYPES.COMPLEX)
        return decomposition.solve(v, trans="H")

    # assign linear operator for inversion
    op = sla.LinearOperator(mat.shape, matvec=fct_matvec, rmatvec=fct_rmatvec, dtype=NP_TYPES.COMPLEX)

    return op


def get_condition_matrix(mat, norm_options):
    """
    Compute an estimate of the condition number (norm 1) of a sparse matrix.
    """

    # get the options
    t_accuracy = norm_options["t_accuracy"]
    n_iter_max = norm_options["n_iter_max"]

    # check shape
    nnz = mat.size
    (nx, ny) = mat.shape

    # check if the matrix is empty
    if (nx, ny) == (0, 0):
        return 0.0

    # display
    logger.debug("matrix size: (%d, %d) / %d" % (nx, ny, nnz))

    # get LU decomposition
    logger.debug("compute LU decomposition")

    decomposition = _get_decomposition(mat)

    # abort if LU decomposition failed
    if decomposition is None:
        logger.warning("condition estimate is infinite")
        return float("inf")

    # get the inverse operator
    op = _get_inverse_operator(mat, decomposition)

    # compute the norm of the matrix inverse (estimate)
    logger.debug("compute estimate norm of the inverse")
    nrm_inv = sla.onenormest(op, t=t_accuracy, itmax=n_iter_max)

    # compute the norm of the matrix (estimate)
    logger.debug("compute estimate norm of the matrix")
    nrm_ori = sla.onenormest(mat, t=t_accuracy, itmax=n_iter_max)

    # compute an estimate of the condition
    logger.debug("compute condition estimate")
    cond = nrm_ori*nrm_inv

    return cond
