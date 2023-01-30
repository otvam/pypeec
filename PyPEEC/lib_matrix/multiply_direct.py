"""
Module for doing matrix-vector multiplication (direct multiplication).
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np
import scipy.linalg as lna


def get_prepare(idx_f, mat):
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

    # assign the elements
    arr = []
    for i in range(nd):
        mat_tmp = mat[:, :, :, i].flatten(order="F")

        mat_dense_tmp = np.zeros((n, n), dtype=np.float64)
        for j in range(n):
            idx_x_tmp = np.abs(idx_x-idx_x[j])
            idx_y_tmp = np.abs(idx_y-idx_y[j])
            idx_z_tmp = np.abs(idx_z-idx_z[j])

            # voxel index number
            idx = idx_x_tmp+idx_y_tmp*nx+idx_z_tmp*nx*ny

            mat_dense_tmp[j] = mat_tmp[idx]

        idx_tmp = np.flatnonzero(np.in1d(np.arange(i*n, (i+1)*n), idx_f))

        mat_dense_tmp = mat_dense_tmp[idx_tmp, :]
        mat_dense_tmp = mat_dense_tmp[:, idx_tmp]
        arr.append(mat_dense_tmp)

    mat_dense2 = lna.block_diag(arr[0], arr[1], arr[2])

    return mat_dense2


def get_multiply(vec_f, mat_dense):
    """
    Matrix-vector multiplication.

    The input vector has the size: n_i.
    The input dense matrix has the size: (n_i, n_i).
    The output vector has the size: n_i.
    """

    res_f = np.matmul(mat_dense, vec_f)

    return res_f
