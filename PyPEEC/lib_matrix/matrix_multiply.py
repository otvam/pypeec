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


def get_prepare(idx_sel, mat, matrix_type):
    """
    Prepare the matrix for the multiplication.
    """

    if MATRIX_MULTIPLICATION == "FFT":
        mat = multiply_fft.get_prepare(mat, matrix_type)
    elif MATRIX_MULTIPLICATION == "DIRECT":
        mat = multiply_direct.get_prepare(idx_sel, mat, matrix_type)
    else:
        raise ValueError("invalid multiplication library")

    return mat


def get_multiply(idx_sel, vec_sel, mat, matrix_type):
    """
    Make a matrix-vector multiplication.
    """

    if MATRIX_MULTIPLICATION == "FFT":
        res_sel = multiply_fft.get_multiply(idx_sel, vec_sel, mat, matrix_type)
    elif MATRIX_MULTIPLICATION == "DIRECT":
        res_sel = multiply_direct.get_multiply(vec_sel, mat)
    else:
        raise ValueError("invalid multiplication library")

    return res_sel
