"""
Module for doing matrix-vector multiplication (direct multiplication).
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np


def _get_voxel_indices(nx, ny, nz):
    """
    Compute the indices of the complete voxel structure.
    """

    # get the indices array
    idx_x = np.arange(nx, dtype=np.int64)
    idx_y = np.arange(ny, dtype=np.int64)
    idx_z = np.arange(nz, dtype=np.int64)
    [idx_x, idx_y, idx_z] = np.meshgrid(idx_x, idx_y, idx_z, indexing="ij")

    # flatten the indices into vectors
    idx_x = idx_x.flatten(order="F")
    idx_y = idx_y.flatten(order="F")
    idx_z = idx_z.flatten(order="F")

    return idx_x, idx_y, idx_z


def _get_dense_zero(n, idx_sel, idx_row, idx_col):
    n_row = np.count_nonzero(np.in1d(np.arange(idx_row*n, (idx_row+1)*n), idx_sel))
    n_col = np.count_nonzero(np.in1d(np.arange(idx_col*n, (idx_col+1)*n), idx_sel))

    mat_dense = np.zeros((n_row, n_col), dtype=np.float64)

    return mat_dense


def _get_dense_diag(idx_sel, mat, idx_row, idx_col, sign_type):
    """
    Construct a dense matrix from a 4D tensor.

    The index vector has the size: n_sel.
    The input tensor has the size: (nx, ny, nz, nd).
    The output dense matrix has the size: (n_sel, n_sel).
    """

    # get the tensor size
    (nx, ny, nz) = mat.shape
    n = nx*ny*nz

    # voxel index array
    (idx_x, idx_y, idx_z) = _get_voxel_indices(nx, ny, nz)

    # get the coefficients
    mat_tmp = mat.flatten(order="F")

    # get the indices of the non-empty face for the current dimension
    idx_row = np.flatnonzero(np.in1d(np.arange(idx_row*n, (idx_row+1)*n), idx_sel))
    idx_col = np.flatnonzero(np.in1d(np.arange(idx_col*n, (idx_col+1)*n), idx_sel))

    # get the tensor indices
    (idx_x_1, idx_x_2) = np.meshgrid(idx_x[idx_row], idx_x[idx_col], indexing="ij")
    (idx_y_1, idx_y_2) = np.meshgrid(idx_y[idx_row], idx_y[idx_col], indexing="ij")
    (idx_z_1, idx_z_2) = np.meshgrid(idx_z[idx_row], idx_z[idx_col], indexing="ij")
    idx_x_tmp = idx_x_1-idx_x_2
    idx_y_tmp = idx_y_1-idx_y_2
    idx_z_tmp = idx_z_1-idx_z_2

    if sign_type == "abs":
        idx_pos = np.full((len(idx_row), len(idx_col)), True, dtype=bool)
    elif sign_type == "x":
        idx_pos = idx_x_tmp >= 0
    elif sign_type == "y":
        idx_pos = idx_y_tmp >= 0
    elif sign_type == "z":
        idx_pos = idx_z_tmp >= 0
    else:
        raise ValueError("invalid sign type")

    # get the sign
    idx_neg = np.logical_not(idx_pos)
    sign = np.empty((len(idx_row), len(idx_col)), dtype=np.int64)
    sign[idx_pos] = +1
    sign[idx_neg] = -1

    # get the distances
    idx_x_tmp = np.abs(idx_x_tmp)
    idx_y_tmp = np.abs(idx_y_tmp)
    idx_z_tmp = np.abs(idx_z_tmp)

    # get the linear indices
    idx = idx_x_tmp+idx_y_tmp*nx+idx_z_tmp*nx*ny

    # assemble the full matrix for the current dimension
    mat_dense = sign*mat_tmp[idx]

    return mat_dense


def get_multiply(vec_sel, mat_dense):
    """
    Matrix-vector multiplication.

    The input vector has the size: n_sel.
    The input dense matrix has the size: (n_sel, n_sel).
    The output vector has the size: n_sel.
    """

    res_sel = np.matmul(mat_dense, vec_sel)

    return res_sel


def get_prepare(idx_sel, mat, matrix_type):
    """
    Construct a dense matrix from a 4D tensor.

    The index vector has the size: n_sel.
    The input tensor has the size: (nx, ny, nz, nd).
    The output dense matrix has the size: (n_sel, n_sel).
    """

    if matrix_type == "3D":
        mat_dense = _get_dense_diag(idx_sel, mat[:, :, :, 0], 0, 0, "abs")
    elif matrix_type == "4D_diag":
        (nx, ny, nz, nd) = mat.shape
        n = nx * ny * nz

        mat_dense_xx = _get_dense_diag(idx_sel, mat[:, :, :, 0], 0, 0, "abs")
        mat_dense_yy = _get_dense_diag(idx_sel, mat[:, :, :, 1], 1, 1, "abs")
        mat_dense_zz = _get_dense_diag(idx_sel, mat[:, :, :, 2], 2, 2, "abs")
        mat_dense_xy = _get_dense_zero(n, idx_sel, 0, 1)
        mat_dense_xz = _get_dense_zero(n, idx_sel, 0, 2)
        mat_dense_yx = _get_dense_zero(n, idx_sel, 1, 0)
        mat_dense_yz = _get_dense_zero(n, idx_sel, 1, 2)
        mat_dense_zx = _get_dense_zero(n, idx_sel, 2, 0)
        mat_dense_zy = _get_dense_zero(n, idx_sel, 2, 1)

        mat_dense = [
            [mat_dense_xx, mat_dense_xy, mat_dense_xz],
            [mat_dense_yx, mat_dense_yy, mat_dense_yz],
            [mat_dense_zx, mat_dense_zy, mat_dense_zz],
        ]
        mat_dense = np.block(mat_dense)
    elif matrix_type == "4D_off":
        (nx, ny, nz, nd) = mat.shape
        n = nx * ny * nz

        mat_dense_xy = _get_dense_diag(idx_sel, mat[:, :, :, 2], 0, 1, "z")
        mat_dense_xz = _get_dense_diag(idx_sel, mat[:, :, :, 1], 0, 2, "y")
        mat_dense_yx = _get_dense_diag(idx_sel, mat[:, :, :, 2], 1, 0, "z")
        mat_dense_yz = _get_dense_diag(idx_sel, mat[:, :, :, 0], 1, 2, "x")
        mat_dense_zx = _get_dense_diag(idx_sel, mat[:, :, :, 1], 2, 0, "y")
        mat_dense_zy = _get_dense_diag(idx_sel, mat[:, :, :, 0], 2, 1, "x")
        mat_dense_xx = _get_dense_zero(n, idx_sel, 0, 0)
        mat_dense_yy = _get_dense_zero(n, idx_sel, 1, 1)
        mat_dense_zz = _get_dense_zero(n, idx_sel, 2, 2)

        mat_dense = [
            [mat_dense_xx, +mat_dense_xy, +mat_dense_xz],
            [-mat_dense_yx, mat_dense_yy, +mat_dense_yz],
            [-mat_dense_zx, -mat_dense_zy, mat_dense_zz],
        ]
        mat_dense = np.block(mat_dense)
    else:
        raise ValueError("invalid matrix type")

    return mat_dense
