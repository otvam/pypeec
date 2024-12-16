"""
Module for estimating the condition number of sparse matrices.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import scilogger
import numpy as np
import scipy.sparse.linalg as sla

# get a logger
LOGGER = scilogger.get_logger(__name__, "pypeec")


def _get_inverse_operator(mat, decomposition):
    """
    Get an inverse operator (with LU decomposition) for the provided matrix and the Hermitian matrix.
    """

    # get the function for the linear operator (original matrix)
    def fct_matvec(rhs):
        sol = decomposition.solve(rhs, trans="N")
        return sol

    # get the function for the linear operator (transposed matrix)
    def fct_rmatvec(rhs):
        sol = decomposition.solve(rhs, trans="H")
        return sol

    # assign linear operator for inversion
    op = sla.LinearOperator(mat.shape, matvec=fct_matvec, rmatvec=fct_rmatvec, dtype=np.complex128)

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
    density = nnz / (nx * ny)

    # display
    LOGGER.debug("matrix size: (%d, %d)" % (nx, ny))
    LOGGER.debug("matrix elements: %d" % nnz)
    LOGGER.debug("matrix density: %.2e" % density)

    # get LU decomposition
    LOGGER.debug("compute LU decomposition")
    decomposition = sla.splu(mat)

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
    cond = nrm_ori * nrm_inv

    return cond


def get_condition_matrix(name, mat, norm_options):
    """
    Compute an estimate of the condition number (norm 1) of a sparse matrix.
    """

    LOGGER.debug("condition: %s" % name)
    with LOGGER.BlockIndent():
        data = _get_condition_matrix_sub(mat, norm_options)

    return data
