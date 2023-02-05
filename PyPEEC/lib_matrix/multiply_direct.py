"""
Module for doing matrix-vector multiplication (direct multiplication).
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np
import scipy.linalg as lna


def _get_dense_diag(idx_sel, mat):
    """
    Construct a dense matrix from a 4D tensor.

    The index vector has the size: n_i.
    The input tensor has the size: (nx, ny, nz, nd).
    The output dense matrix has the size: (n_i, n_i).
    """

    # get the tensor size
    (nx, ny, nz, nd) = mat.shape
    n = nx*ny*nz

    # voxel index array
    idx_x = np.arange(nx, dtype=np.int64)
    idx_y = np.arange(ny, dtype=np.int64)
    idx_z = np.arange(nz, dtype=np.int64)
    (idx_x, idx_y, idx_z) = np.meshgrid(idx_x, idx_y, idx_z, indexing="ij")
    idx_x = idx_x.flatten(order="F")
    idx_y = idx_y.flatten(order="F")
    idx_z = idx_z.flatten(order="F")

    # array for the matrix along each dimension
    mat_list = []

    # assign the dense matrix for each dimension
    for i in range(nd):
        # get the coefficients
        mat_tmp = mat[:, :, :, i].flatten(order="F")

        # get the indices of the non-empty face for the current dimension
        idx_tmp = np.flatnonzero(np.in1d(np.arange(i*n, (i+1)*n), idx_sel))
        idx_x_tmp = idx_x[idx_tmp]
        idx_y_tmp = idx_y[idx_tmp]
        idx_z_tmp = idx_z[idx_tmp]

        # get the tensor indices
        (idx_x_1, idx_x_2) = np.meshgrid(idx_x_tmp, idx_x_tmp, indexing="ij")
        (idx_y_1, idx_y_2) = np.meshgrid(idx_y_tmp, idx_y_tmp, indexing="ij")
        (idx_z_1, idx_z_2) = np.meshgrid(idx_z_tmp, idx_z_tmp, indexing="ij")
        idx_x_tmp = np.abs(idx_x_1-idx_x_2)
        idx_y_tmp = np.abs(idx_y_1-idx_y_2)
        idx_z_tmp = np.abs(idx_z_1-idx_z_2)

        # get the linear indices
        idx = idx_x_tmp+idx_y_tmp*nx+idx_z_tmp*nx*ny

        # assemble the full matrix for the current dimension
        mat_dense_tmp = mat_tmp[idx]

        # append to the list containing all the dimensions
        mat_list.append(mat_dense_tmp)

    # construct the block diagonal matrix
    mat_dense = lna.block_diag(*mat_list)

    return mat_dense


def get_multiply(vec_sel, mat_dense):
    """
    Matrix-vector multiplication.

    The input vector has the size: n_i.
    The input dense matrix has the size: (n_i, n_i).
    The output vector has the size: n_i.
    """

    res_sel = np.matmul(mat_dense, vec_sel)

    return res_sel


def get_prepare(idx_sel, mat, matrix_type):
    """
    Construct a dense matrix from a 4D tensor.

    The index vector has the size: n_i.
    The input tensor has the size: (nx, ny, nz, nd).
    The output dense matrix has the size: (n_i, n_i).
    """

    if matrix_type == "3D":
        mat = np.expand_dims(mat, axis=3)
        mat_dense = _get_dense_diag(idx_sel, mat)
    elif matrix_type == "4D_diag":
        mat_dense = _get_dense_diag(idx_sel, mat)
    else:
        raise ValueError("invallid matrix type")

    return mat_dense
