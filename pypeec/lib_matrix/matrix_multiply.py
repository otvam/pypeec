"""
Module for doing matrix-vector multiplication:
    - Using standard matrix multiplication.
    - Using circulant tensors and FFTs.

Three different types of matrices are supported:
    - Tensor representing a simple potential matrix.
        - Size of the last dimension of the input tensor: 1.
        - Number of dimensions of the input vector: 1.
        - Number of dimensions of the output vector: 1.
    - Tensor representing a block diagonal inductance matrix.
        - Size of the last dimension of the input tensor: 1.
        - Number of dimensions of the input vector: 3.
        - Number of dimensions of the output vector: 3.
    - Tensor representing a block off-diagonal coupling matrix.
        - Size of the last dimension of the input tensor: 3.
        - Number of dimensions of the input vector: 3.
        - Number of dimensions of the output vector: 3.

A matrix-vector operator is returned for performing the matrix-vector multiplication:
    - For standard multiplication, the full matrix is constructed and stored.
    - For FFT multiplication, the full matrix is never constructed nor stored.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

from pypeec.lib_matrix import multiply_fft
from pypeec.lib_matrix import multiply_dense


def _get_multiply(data, vec_in, dense_options, flip):
    """
    Make a matrix-vector multiplication.
    """

    # extract the data
    split = dense_options["split"]
    method = dense_options["method"]
    fft_options = dense_options["fft_options"]

    # multiply the matrix
    if method == "fft":
        res_out = multiply_fft.get_multiply(data, vec_in, split, fft_options, flip)
    elif method == "dense":
        res_out = multiply_dense.get_multiply(data, vec_in, flip)
    else:
        raise ValueError("invalid multiplication library")

    return res_out


def _get_prepare(name, idx_out, idx_in, mat, dense_options):
    """
    Prepare the matrix for the multiplication.
    """

    # extract the data
    split = dense_options["split"]
    method = dense_options["method"]
    fft_options = dense_options["fft_options"]

    # prepare the matrix
    if method == "fft":
        data = multiply_fft.get_prepare(name, idx_out, idx_in, mat, split, fft_options)
    elif method == "dense":
        data = multiply_dense.get_prepare(name, idx_out, idx_in, mat)
    else:
        raise ValueError("invalid multiplication library")

    return data


def get_operator_potential(idx, mat, dense_options):
    """
    Get the linear matrix-vector operator for a simple potential matrix.
    """

    # prepare the matrix
    data = _get_prepare("potential", idx, idx, mat, dense_options)

    # function describing the matrix-vector multiplication
    def op(vec_in):
        res_out = _get_multiply(data, vec_in, dense_options, False)
        return res_out

    return op


def get_operator_inductance(idx, mat, dense_options):
    """
    Get the linear matrix-vector operator for a block diagonal inductance matrix.
    """

    # prepare the matrix
    data = _get_prepare("inductance", idx, idx, mat, dense_options)

    # function describing the matrix-vector multiplication
    def op(vec_in):
        res_out = _get_multiply(data, vec_in, dense_options, False)
        return res_out

    return op


def get_operator_coupling(idx_out, idx_in, mat, dense_options):
    """
    Get the linear matrix-vector operator for a block off-diagonal coupling matrix.
    """

    # prepare the matrix
    data = _get_prepare("coupling", idx_out, idx_in, mat, dense_options)

    # function describing the matrix-vector multiplication
    def op_for(vec_in):
        res_out = _get_multiply(data, vec_in, dense_options, False)
        return res_out

    # function describing the matrix-vector multiplication
    def op_rev(vec_in):
        res_out = _get_multiply(data, vec_in, dense_options, True)
        return res_out

    return op_for, op_rev
