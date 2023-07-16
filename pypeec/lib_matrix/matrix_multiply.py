"""
Module for doing matrix-vector multiplication:
    - direct matrix multiplication
    - multiplication with FFT and circulant tensors

Three different types of matrices are supported:
    - potential: tensor representing a simple potential matrix
        - size of the last dimension of the input tensor = 1
        - number of dimensions of the input vector = 1
        - number of dimensions of the output vector = 1
    - inductance: tensor representing a block diagonal inductance matrix
        - size of the last dimension of the input tensor = 1
        - number of dimensions of the input vector = 3
        - number of dimensions of the output vector = 3
    - coupling: tensor representing a block off-diagonal coupling matrix
        - size of the last dimension of the input tensor = 3
        - number of dimensions of the input vector = 3
        - number of dimensions of the output vector = 3

A matrix-vector operator is returned for performing the matrix-vector multiplication.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

from pypeec.lib_matrix import multiply_fft
from pypeec.lib_matrix import multiply_direct
from pypeec import config

# get config
MATRIX_MULTIPLICATION = config.MATRIX_MULTIPLICATION


def _get_multiply(data, vec_in, flip):
    """
    Make a matrix-vector multiplication.
    """

    if MATRIX_MULTIPLICATION == "FFT":
        res_out = multiply_fft.get_multiply(data, vec_in, flip)
    elif MATRIX_MULTIPLICATION == "DIRECT":
        res_out = multiply_direct.get_multiply(data, vec_in, flip)
    else:
        raise ValueError("invalid multiplication library")

    return res_out


def _get_prepare(name, idx_out, idx_in, mat):
    """
    Prepare the matrix for the multiplication.
    """

    if MATRIX_MULTIPLICATION == "FFT":
        data = multiply_fft.get_prepare(name, idx_out, idx_in, mat)
    elif MATRIX_MULTIPLICATION == "DIRECT":
        data = multiply_direct.get_prepare(name, idx_out, idx_in, mat)
    else:
        raise ValueError("invalid multiplication library")

    return data


def get_operator_potential(idx, mat):
    """
    Get the linear matrix-vector operator for a simple potential matrix.
    """

    # prepare the matrix
    data = _get_prepare("potential", idx, idx, mat)

    # function describing the matrix-vector multiplication
    def op(vec_in):
        res_out = _get_multiply(data, vec_in, False)
        return res_out

    return op


def get_operator_inductance(idx, mat):
    """
    Get the linear matrix-vector operator for a block diagonal inductance matrix.
    """

    # prepare the matrix
    data = _get_prepare("inductance", idx, idx, mat)

    # function describing the matrix-vector multiplication
    def op(vec_in):
        res_out = _get_multiply(data, vec_in, False)
        return res_out

    return op


def get_operator_coupling(idx_out, idx_in, mat):
    """
    Get the linear matrix-vector operator for a block off-diagonal coupling matrix.
    """

    # prepare the matrix
    data = _get_prepare("coupling", idx_out, idx_in, mat)

    # function describing the matrix-vector multiplication
    def op_for(vec_in):
        res_out = _get_multiply(data, vec_in, False)
        return res_out

    # function describing the matrix-vector multiplication
    def op_rev(vec_in):
        res_out = _get_multiply(data, vec_in, True)
        return res_out

    return op_for, op_rev
