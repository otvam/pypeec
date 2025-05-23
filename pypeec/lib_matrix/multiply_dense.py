"""
Module for doing matrix-vector multiplication (direct multiplication).
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import scilogger
import numpy as np

# get a logger
LOGGER = scilogger.get_logger(__name__, "pypeec")


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


def _get_dense_zero(idx_out, idx_in, mat, idx_row, idx_col):
    """
    Construct a zero matrix for a given block position.
    """

    # extract the voxel data
    (nx, ny, nz, nd) = mat.shape
    nv = nx * ny * nz

    # get the matrix size
    idx_row = np.isin(np.arange(idx_row * nv, (idx_row + 1) * nv, dtype=np.int64), idx_out)
    idx_col = np.isin(np.arange(idx_col * nv, (idx_col + 1) * nv, dtype=np.int64), idx_in)
    n_row = np.count_nonzero(idx_row)
    n_col = np.count_nonzero(idx_col)

    # create an empty matrix
    data = np.zeros((n_row, n_col), dtype=np.float64)

    return data


def _get_dense_diag(idx_out, idx_in, mat, idx_row, idx_col, sign_type):
    """
    Construct a dense matrix from a tensor for a given block position.
    """

    # get the tensor size
    (nx, ny, nz) = mat.shape
    nv = nx * ny * nz

    # voxel index array
    (idx_x, idx_y, idx_z) = _get_voxel_indices(nx, ny, nz)

    # get the indices of the non-empty face for the current dimension
    idx_row = np.isin(np.arange(idx_row * nv, (idx_row + 1) * nv, dtype=np.int64), idx_out)
    idx_col = np.isin(np.arange(idx_col * nv, (idx_col + 1) * nv, dtype=np.int64), idx_in)
    n_row = np.count_nonzero(idx_row)
    n_col = np.count_nonzero(idx_col)

    # get the relative position between elements
    (idx_x_1, idx_x_2) = np.meshgrid(idx_x[idx_row], idx_x[idx_col], indexing="ij")
    (idx_y_1, idx_y_2) = np.meshgrid(idx_y[idx_row], idx_y[idx_col], indexing="ij")
    (idx_z_1, idx_z_2) = np.meshgrid(idx_z[idx_row], idx_z[idx_col], indexing="ij")
    idx_x_tmp = idx_x_1 - idx_x_2
    idx_y_tmp = idx_y_1 - idx_y_2
    idx_z_tmp = idx_z_1 - idx_z_2

    # select the element with a positive sign
    if sign_type == "abs":
        idx_pos = np.full((n_row, n_col), True, dtype=bool)
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
    sign = np.empty((n_row, n_col), dtype=np.int64)
    sign[idx_pos] = +1
    sign[idx_neg] = -1

    # get the tensor indices
    idx_x_tmp = np.abs(idx_x_tmp)
    idx_y_tmp = np.abs(idx_y_tmp)
    idx_z_tmp = np.abs(idx_z_tmp)

    # get the linear indices
    idx = idx_x_tmp + idx_y_tmp * nx + idx_z_tmp * nx * ny

    # get the coefficients
    mat_tmp = mat.flatten(order="F")

    # assemble the full matrix for the current dimension
    data = sign * mat_tmp[idx]

    return data


def get_prepare(name, idx_out, idx_in, mat):
    """
    Construct a dense matrix from a 4D tensor (main function).

    The output index vector has the size: n_out.
    The input index vector has the size: n_in.
    The output dense matrix has the size: (n_out, n_in).
    """

    # get the matrix size
    n_out = len(idx_out)
    n_in = len(idx_in)
    itemsize = np.dtype(np.float64).itemsize
    footprint = (itemsize * n_out * n_in) / (1024**2)

    # display the matrix size
    LOGGER.debug("%s / footprint =  %.2f MB", name, footprint)

    # get the permutation for sorting
    idx_perm_out = np.argsort(idx_out)
    idx_perm_in = np.argsort(idx_in)
    idx_rev_out = np.empty(len(idx_perm_out), dtype=np.int64)
    idx_rev_in = np.empty(len(idx_perm_in), dtype=np.int64)
    idx_rev_out[idx_perm_out] = np.arange(len(idx_perm_out), dtype=np.int64)
    idx_rev_in[idx_perm_in] = np.arange(len(idx_perm_in), dtype=np.int64)

    # sort the indices
    idx_out = idx_out[idx_perm_out]
    idx_in = idx_in[idx_perm_in]

    # get the matrix (sorted indices)
    if name == "potential":
        data = _get_dense_diag(idx_out, idx_in, mat[:, :, :, 0], 0, 0, "abs")
    elif name == "inductance":
        # fill the diagonal blocks
        data_xx = _get_dense_diag(idx_out, idx_in, mat[:, :, :, 0], 0, 0, "abs")
        data_yy = _get_dense_diag(idx_out, idx_in, mat[:, :, :, 0], 1, 1, "abs")
        data_zz = _get_dense_diag(idx_out, idx_in, mat[:, :, :, 0], 2, 2, "abs")

        # the off-diagonal blocks are empty
        data_xy = _get_dense_zero(idx_out, idx_in, mat, 0, 1)
        data_xz = _get_dense_zero(idx_out, idx_in, mat, 0, 2)
        data_yx = _get_dense_zero(idx_out, idx_in, mat, 1, 0)
        data_yz = _get_dense_zero(idx_out, idx_in, mat, 1, 2)
        data_zx = _get_dense_zero(idx_out, idx_in, mat, 2, 0)
        data_zy = _get_dense_zero(idx_out, idx_in, mat, 2, 1)

        # assemble the matrix from the blocks
        data = [
            [data_xx, data_xy, data_xz],
            [data_yx, data_yy, data_yz],
            [data_zx, data_zy, data_zz],
        ]
        data = np.block(data)
    elif name == "coupling":
        # fill the off-diagonal blocks
        data_xy = _get_dense_diag(idx_out, idx_in, mat[:, :, :, 2], 0, 1, "z")
        data_xz = _get_dense_diag(idx_out, idx_in, mat[:, :, :, 1], 0, 2, "y")
        data_yx = _get_dense_diag(idx_out, idx_in, mat[:, :, :, 2], 1, 0, "z")
        data_yz = _get_dense_diag(idx_out, idx_in, mat[:, :, :, 0], 1, 2, "x")
        data_zx = _get_dense_diag(idx_out, idx_in, mat[:, :, :, 1], 2, 0, "y")
        data_zy = _get_dense_diag(idx_out, idx_in, mat[:, :, :, 0], 2, 1, "x")

        # the diagonal blocks are empty
        data_xx = _get_dense_zero(idx_out, idx_in, mat, 0, 0)
        data_yy = _get_dense_zero(idx_out, idx_in, mat, 1, 1)
        data_zz = _get_dense_zero(idx_out, idx_in, mat, 2, 2)

        # assemble the matrix from the blocks
        data = [
            [data_xx, +data_xy, +data_xz],
            [-data_yx, data_yy, +data_yz],
            [-data_zx, -data_zy, data_zz],
        ]
        data = np.block(data)
    else:
        raise ValueError("invalid matrix type")

    # restore the original indices order
    data = data[idx_rev_out, :]
    data = data[:, idx_rev_in]

    return data


def get_multiply(data, vec_in, flip):
    """
    Matrix-vector multiplication.
    If the flip switch is activated, the input and output are flipped.

    The input vector has the size: n_in.
    The input dense matrix has the size: (n_out, n_in).
    The output vector has the size: n_out.
    """

    if flip:
        res_out = np.matmul(vec_in, data)
    else:
        res_out = np.matmul(data, vec_in)

    return res_out
