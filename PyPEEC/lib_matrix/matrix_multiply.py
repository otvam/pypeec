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

import scipy.sparse.linalg as sla
from PyPEEC.lib_matrix import multiply_fft
from PyPEEC.lib_matrix import multiply_direct
from PyPEEC import config

# get config
MATRIX_MULTIPLICATION = config.MATRIX_MULTIPLICATION


def _get_multiply(idx_out, idx_in, vec_in, mat, matrix_type):
    """
    Make a matrix-vector multiplication.
    """

    if MATRIX_MULTIPLICATION == "FFT":
        res_out = multiply_fft.get_multiply(idx_out, idx_in, vec_in, mat, matrix_type)
    elif MATRIX_MULTIPLICATION == "DIRECT":
        res_out = multiply_direct.get_multiply(vec_in, mat)
    else:
        raise ValueError("invalid multiplication library")

    return res_out


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

    # function describing the matrix-vector multiplication
    def fct(vec_in):
        res_out = _get_multiply(idx_out, idx_in, vec_in, mat, matrix_type)
        return res_out

    # corresponding linear operator
    op = sla.LinearOperator((len(idx_out), len(idx_in)), matvec=fct)

    return op


def get_operator_single(idx, mat):
    """
    Prepare a single matrix for the multiplication.
    """

    op = _get_prepare(idx, idx, mat, "single")

    return op


def get_operator_diag(idx, mat):
    """
    Prepare a diagonal matrix for the multiplication.
    """

    op = _get_prepare(idx, idx, mat, "diag")

    return op


def get_operator_cross(idx_out, idx_in, mat):
    """
    Prepare a cross matrix for the multiplication.
    """

    op = _get_prepare(idx_out, idx_in, mat, "cross")

    return op
