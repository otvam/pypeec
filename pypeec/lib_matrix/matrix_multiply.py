"""
Module for doing matrix-vector multiplication:
    - direct matrix multiplication
    - multiplication with FFT and circulant tensors

Three different types of matrices are supported:
    - single: tensor representing a simple matrix
        - number of dimensions of the input matrix = 1
        - number of dimensions of the input vector = 1
    - diag: tensor representing a block diagonal matrix
        - number of dimensions of the input matrix = 1
        - number of dimensions of the input vector = 3
    - cross: tensor representing a block off-diagonal matrix
        - number of dimensions of the input matrix = 3
        - number of dimensions of the input vector = 3

A matrix-vector operator is returned for performing the matrix-vector multiplication.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

from pypeec.lib_matrix import multiply_fft
from pypeec.lib_matrix import multiply_direct
from pypeec import config

# get config
MATRIX_MULTIPLICATION = config.MATRIX_MULTIPLICATION


def _get_multiply(data, vec_in, matrix_type, flip):
    """
    Make a matrix-vector multiplication.
    """

    if MATRIX_MULTIPLICATION == "FFT":
        res_out = multiply_fft.get_multiply(data, vec_in, matrix_type, flip)
    elif MATRIX_MULTIPLICATION == "DIRECT":
        res_out = multiply_direct.get_multiply(data, vec_in, flip)
    else:
        raise ValueError("invalid multiplication library")

    return res_out


def _get_prepare(idx_out, idx_in, mat, matrix_type):
    """
    Prepare the matrix for the multiplication.
    """

    # get the matrix
    if MATRIX_MULTIPLICATION == "FFT":
        data = multiply_fft.get_prepare(idx_out, idx_in, mat, matrix_type)
    elif MATRIX_MULTIPLICATION == "DIRECT":
        data = multiply_direct.get_prepare(idx_out, idx_in, mat, matrix_type)
    else:
        raise ValueError("invalid multiplication library")

    return data


def get_operator_single(idx, mat):
    """
    Get the linear matrix-vector operator for a single-type matrix.
    """

    # prepare the matrix
    data = _get_prepare(idx, idx, mat, "single")

    # function describing the matrix-vector multiplication
    def op(vec_in):
        res_out = _get_multiply(data, vec_in, "single", False)
        return res_out

    return op


def get_operator_diag(idx, mat):
    """
    Get the linear matrix-vector operator for a diagonal-type matrix.
    """

    # prepare the matrix
    data = _get_prepare(idx, idx, mat, "diag")

    # function describing the matrix-vector multiplication
    def op(vec_in):
        res_out = _get_multiply(data, vec_in, "diag", False)
        return res_out

    return op


def get_operator_cross(idx_out, idx_in, mat):
    """
    Get the linear matrix-vector operator for a cross-type matrix.
    """

    # prepare the matrix
    data = _get_prepare(idx_out, idx_in, mat, "cross")

    # function describing the matrix-vector multiplication
    def op_for(vec_in):
        res_out = _get_multiply(data, vec_in, "cross", False)
        return res_out

    # function describing the matrix-vector multiplication
    def op_rev(vec_in):
        res_out = _get_multiply(data, vec_in, "cross", True)
        return res_out

    return op_for, op_rev
