"""
Module for doing matrix-vector multiplication:
    - direct matrix multiplication
    - multiplication with FFT and circulant tensors

Three different types of matrices are supported:
    - single: tensor representing a simple matrix (nd = 1)
    - diag: tensor representing a block diagonal matrix (nd = 3)
    - cross: tensor representing a block off-diagonal matrix (nd = 3)
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

from PyPEEC.lib_matrix import multiply_fft
from PyPEEC.lib_matrix import multiply_direct
from PyPEEC import config

# get config
MATRIX_MULTIPLICATION = config.MATRIX_MULTIPLICATION


def _get_prepare(idx_out, idx_in, mat, matrix_type):
    """
    Prepare the matrix for the multiplication.
    """

    # get the matrix
    if MATRIX_MULTIPLICATION == "FFT":
        mat = multiply_fft.get_prepare(mat, matrix_type)
    elif MATRIX_MULTIPLICATION == "DIRECT":
        mat = multiply_direct.get_prepare(idx_out, idx_in, mat, matrix_type)
    else:
        raise ValueError("invalid multiplication library")

    # assign the properties
    data = {"mat": mat, "idx_out": idx_out, "idx_in": idx_in, "matrix_type": matrix_type}

    return data


def _get_multiply(idx_out, idx_in, vec_in, mat, matrix_type):
    """
    Make a matrix-vector multiplication.
    """

    if MATRIX_MULTIPLICATION == "FFT":
        res_sel = multiply_fft.get_multiply(idx_out, idx_in, vec_in, mat, matrix_type)
    elif MATRIX_MULTIPLICATION == "DIRECT":
        res_sel = multiply_direct.get_multiply(vec_in, mat)
    else:
        raise ValueError("invalid multiplication library")

    return res_sel


def get_prepare_single(idx, mat):
    """
    Prepare a single matrix for the multiplication.
    """

    mat = _get_prepare(idx, idx, mat, "single")

    return mat


def get_prepare_diag(idx, mat):
    """
    Prepare a diagonal matrix for the multiplication.
    """

    mat = _get_prepare(idx, idx, mat, "diag")

    return mat


def get_prepare_cross(idx_out, idx_in, mat):
    """
    Prepare a cross matrix for the multiplication.
    """

    mat = _get_prepare(idx_out, idx_in, mat, "cross")

    return mat


def get_multiply(data, vec_in):
    """
    Make a matrix-vector multiplication.
    """

    # extract the data
    mat = data["mat"]
    idx_out = data["idx_out"]
    idx_in = data["idx_in"]
    matrix_type = data["matrix_type"]

    # get the multiplication
    res = _get_multiply(idx_out, idx_in, vec_in, mat, matrix_type)

    return res
