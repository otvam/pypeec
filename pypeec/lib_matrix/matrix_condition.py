"""
Module for estimating the condition number of sparse matrices.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import scipy.sparse.linalg as sla
from pypeec import log
from pypeec import config

# get a logger
LOGGER = log.get_logger("COND")

# get config
NP_TYPES = config.NP_TYPES


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
    def fct_matvec(rhs):
        rhs = rhs.astype(NP_TYPES.COMPLEX)
        sol = decomposition.solve(rhs, trans="N")
        return sol

    # get the function for the linear operator (transposed matrix)
    def fct_rmatvec(rhs):
        rhs = rhs.astype(NP_TYPES.COMPLEX)
        sol = decomposition.solve(rhs, trans="H")
        return sol

    # assign linear operator for inversion
    op = sla.LinearOperator(mat.shape, matvec=fct_matvec, rmatvec=fct_rmatvec, dtype=NP_TYPES.COMPLEX)

    return op


def _get_condition_matrix_sub(mat, norm_options):
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

    # compute matrix density
    density = nnz/(nx*ny)

    # display
    LOGGER.debug("matrix size: (%d, %d)" % (nx, ny))
    LOGGER.debug("matrix elements: %d" % nnz)
    LOGGER.debug("matrix density: %.2e" % density)

    # get LU decomposition
    LOGGER.debug("compute LU decomposition")
    decomposition = _get_decomposition(mat)

    # abort if LU decomposition failed
    if decomposition is None:
        LOGGER.warning("condition estimate is infinite")
        return float("inf")

    # get the inverse operator
    op = _get_inverse_operator(mat, decomposition)

    # compute the norm of the matrix inverse (estimate)
    LOGGER.debug("estimate norm of the inverse")
    nrm_inv = sla.onenormest(op, t=t_accuracy, itmax=n_iter_max)

    # compute the norm of the matrix (estimate)
    LOGGER.debug("estimate norm of the matrix")
    nrm_ori = sla.onenormest(mat, t=t_accuracy, itmax=n_iter_max)

    # compute an estimate of the condition
    LOGGER.debug("compute condition estimate")
    cond = nrm_ori*nrm_inv

    return cond


def get_condition_matrix(name, mat, norm_options):
    """
    Compute an estimate of the condition number (norm 1) of a sparse matrix.
    """

    LOGGER.debug("condition: %s" % name)
    with log.BlockIndent():
        data = _get_condition_matrix_sub(mat, norm_options)

    return data
