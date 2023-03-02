"""
Module for doing matrix-vector multiplication (direct multiplication).

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
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import numpy as np


def _get_voxel_indices(nx, ny, nz):
    """
    Compute the indices of the complete voxel structure.
    """

    # get the indices array
    idx_x = np.arange(nx, dtype=np.int_)
    idx_y = np.arange(ny, dtype=np.int_)
    idx_z = np.arange(nz, dtype=np.int_)
    [idx_x, idx_y, idx_z] = np.meshgrid(idx_x, idx_y, idx_z, indexing="ij")

    # flatten the indices into vectors
    idx_x = idx_x.flatten(order="F")
    idx_y = idx_y.flatten(order="F")
    idx_z = idx_z.flatten(order="F")

    return idx_x, idx_y, idx_z


def _get_dense_zero(idx_out, idx_in, mat, idx_row, idx_col):
    """
    Construct a zero matrix for a given block position.
    """

    # get the
    (nx, ny, nz, nd) = mat.shape
    nv = nx*ny*nz

    # get the matrix size
    n_row = np.count_nonzero(np.in1d(np.arange(idx_row*nv, (idx_row+1)*nv), idx_out))
    n_col = np.count_nonzero(np.in1d(np.arange(idx_col*nv, (idx_col+1)*nv), idx_in))

    # create an empty matrix
    mat_dense = np.zeros((n_row, n_col), dtype=np.float_)

    return mat_dense


def _get_dense_diag(idx_out, idx_in, mat, idx_row, idx_col, sign_type):
    """
    Construct a dense matrix from a tensor for a given block position.
    """

    # get the tensor size
    (nx, ny, nz) = mat.shape
    nv = nx*ny*nz

    # voxel index array
    (idx_x, idx_y, idx_z) = _get_voxel_indices(nx, ny, nz)

    # get the coefficients
    mat_tmp = mat.flatten(order="F")

    # get the indices of the non-empty face for the current dimension
    idx_row = np.flatnonzero(np.in1d(np.arange(idx_row*nv, (idx_row+1)*nv), idx_out))
    idx_col = np.flatnonzero(np.in1d(np.arange(idx_col*nv, (idx_col+1)*nv), idx_in))

    # get the relative position between elements
    (idx_x_1, idx_x_2) = np.meshgrid(idx_x[idx_row], idx_x[idx_col], indexing="ij")
    (idx_y_1, idx_y_2) = np.meshgrid(idx_y[idx_row], idx_y[idx_col], indexing="ij")
    (idx_z_1, idx_z_2) = np.meshgrid(idx_z[idx_row], idx_z[idx_col], indexing="ij")
    idx_x_tmp = idx_x_1-idx_x_2
    idx_y_tmp = idx_y_1-idx_y_2
    idx_z_tmp = idx_z_1-idx_z_2

    # select the element with a positive sign
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

    # get the sign matrix
    idx_neg = np.logical_not(idx_pos)
    sign = np.empty((len(idx_row), len(idx_col)), dtype=np.int_)
    sign[idx_pos] = +1
    sign[idx_neg] = -1

    # get the tensor indices
    idx_x_tmp = np.abs(idx_x_tmp)
    idx_y_tmp = np.abs(idx_y_tmp)
    idx_z_tmp = np.abs(idx_z_tmp)

    # get the linear indices
    idx = idx_x_tmp+idx_y_tmp*nx+idx_z_tmp*nx*ny

    # assemble the full matrix for the current dimension
    mat_dense = sign*mat_tmp[idx]

    return mat_dense


def get_prepare(idx_out, idx_in, mat, matrix_type):
    """
    Construct a dense matrix from a 4D tensor.

    The output index vector has the size: n_out.
    The input index vector has the size: n_in.
    The output dense matrix has the size: (n_out, n_in).
    """

    # get the permutation for sorting
    idx_perm_out = np.argsort(idx_out)
    idx_perm_in = np.argsort(idx_in)
    idx_rev_out = np.empty(len(idx_perm_out), dtype=np.int_)
    idx_rev_in = np.empty(len(idx_perm_in), dtype=np.int_)
    idx_rev_out[idx_perm_out] = np.arange(len(idx_perm_out))
    idx_rev_in[idx_perm_in] = np.arange(len(idx_perm_in))

    # sort the indices
    idx_out = idx_out[idx_perm_out]
    idx_in = idx_in[idx_perm_in]

    # get the matrix (sorted indices)
    if matrix_type == "single":
        mat_dense = _get_dense_diag(idx_out, idx_in, mat[:, :, :, 0], 0, 0, "abs")
    elif matrix_type == "diag":
        # fill the diagonal blocks
        mat_dense_xx = _get_dense_diag(idx_out, idx_in, mat[:, :, :, 0], 0, 0, "abs")
        mat_dense_yy = _get_dense_diag(idx_out, idx_in, mat[:, :, :, 0], 1, 1, "abs")
        mat_dense_zz = _get_dense_diag(idx_out, idx_in, mat[:, :, :, 0], 2, 2, "abs")

        # the off-diagonal blocks are empty
        mat_dense_xy = _get_dense_zero(idx_out, idx_in, mat, 0, 1)
        mat_dense_xz = _get_dense_zero(idx_out, idx_in, mat, 0, 2)
        mat_dense_yx = _get_dense_zero(idx_out, idx_in, mat, 1, 0)
        mat_dense_yz = _get_dense_zero(idx_out, idx_in, mat, 1, 2)
        mat_dense_zx = _get_dense_zero(idx_out, idx_in, mat, 2, 0)
        mat_dense_zy = _get_dense_zero(idx_out, idx_in, mat, 2, 1)

        # assemble the matrix from the blocks
        mat_dense = [
            [mat_dense_xx, mat_dense_xy, mat_dense_xz],
            [mat_dense_yx, mat_dense_yy, mat_dense_yz],
            [mat_dense_zx, mat_dense_zy, mat_dense_zz],
        ]
        mat_dense = np.block(mat_dense)
    elif matrix_type == "cross":
        # fill the off-diagonal blocks
        mat_dense_xy = _get_dense_diag(idx_out, idx_in, mat[:, :, :, 2], 0, 1, "z")
        mat_dense_xz = _get_dense_diag(idx_out, idx_in, mat[:, :, :, 1], 0, 2, "y")
        mat_dense_yx = _get_dense_diag(idx_out, idx_in, mat[:, :, :, 2], 1, 0, "z")
        mat_dense_yz = _get_dense_diag(idx_out, idx_in, mat[:, :, :, 0], 1, 2, "x")
        mat_dense_zx = _get_dense_diag(idx_out, idx_in, mat[:, :, :, 1], 2, 0, "y")
        mat_dense_zy = _get_dense_diag(idx_out, idx_in, mat[:, :, :, 0], 2, 1, "x")

        # the diagonal blocks are empty
        mat_dense_xx = _get_dense_zero(idx_out, idx_in, mat, 0, 0)
        mat_dense_yy = _get_dense_zero(idx_out, idx_in, mat, 1, 1)
        mat_dense_zz = _get_dense_zero(idx_out, idx_in, mat, 2, 2)

        # assemble the matrix from the blocks
        mat_dense = [
            [mat_dense_xx, +mat_dense_xy, +mat_dense_xz],
            [-mat_dense_yx, mat_dense_yy, +mat_dense_yz],
            [-mat_dense_zx, -mat_dense_zy, mat_dense_zz],
        ]
        mat_dense = np.block(mat_dense)
    else:
        raise ValueError("invalid matrix type")

    # restore the original indices order
    mat_dense = mat_dense[idx_rev_out, :]
    mat_dense = mat_dense[:, idx_rev_in]

    return mat_dense


def get_multiply(mat_dense, vec_in, flip):
    """
    Matrix-vector multiplication.
    If the flip switch is activated, the input and output are flipped.

    The input vector has the size: n_in.
    The input dense matrix has the size: (n_out, n_in).
    The output vector has the size: n_out.
    """

    if flip:
        res_out = np.matmul(vec_in, mat_dense)
    else:
        res_out = np.matmul(mat_dense, vec_in)

    return res_out
