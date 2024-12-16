"""
Different functions for dealing the voxel data.
Compute the voxel coordinates and the incidence matrix.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import numpy as np
import scipy.sparse as sps


def get_voxel_coordinate(n, d, c):
    """
    Get the coordinate of the different voxels.
    The center voxel center is at the specified origin coordinate.

    The voxel structure has the following size: (nx, ny, nz).
    The array has the following dimension: (nx*ny*nz, 3).
    """

    # cast to array
    c = np.array(c, dtype=np.float64)
    d = np.array(d, dtype=np.float64)
    n = np.array(n, dtype=np.int64)

    # get total size
    nv = np.prod(n)

    # all the indices
    idx_linear = np.arange(0, nv, dtype=np.int64)

    # convert linear indices into tensor indices
    (idx_x, idx_y, idx_z) = np.unravel_index(idx_linear, n, order="F")

    # assemble the coordinate array
    idx_vox = np.stack((idx_x, idx_y, idx_z), axis=1)

    # origin coordinate
    o = c - (n * d) / 2

    # assemble the coordinate array
    pts_vox = o + d / 2 + d * idx_vox

    return pts_vox


def get_incidence_matrix(n):
    """
    Get the incidence matrix of the voxel structure.
    This matrix describes the relation between the voxels and the faces.

    The voxel structure has the following size: (nx, ny, nz).
    The matrix has the following dimension: (nx*ny*nz, 3*nx*ny*nz).
    The columns represent the face with the following order: x, y, and, z.
    The rows represent the voxels.
    """

    # extract the voxel data
    (nx, ny, nz) = n

    # get total size
    nv = np.prod(n)

    # voxel index array
    x = np.arange(nx, dtype=np.int64)
    y = np.arange(ny, dtype=np.int64)
    z = np.arange(nz, dtype=np.int64)
    (idx_x, idx_y, idx_z) = np.meshgrid(x, y, z, indexing="ij")

    # voxel index number
    idx = idx_x + idx_y * nx + idx_z * nx * ny

    # create the sparse matrix
    A_vox = sps.csc_matrix((nv, 3 * nv), dtype=np.int64)

    # assign the diagonal, each voxel is connected to three faces with positive indices
    data = np.ones(nv, dtype=np.int64)
    idx_row_col = np.arange(nv, dtype=np.int64)
    A_vox += sps.csc_matrix((data, (idx_row_col, 0 * nv + idx_row_col)), shape=(nv, 3 * nv), dtype=np.int64)
    A_vox += sps.csc_matrix((data, (idx_row_col, 1 * nv + idx_row_col)), shape=(nv, 3 * nv), dtype=np.int64)
    A_vox += sps.csc_matrix((data, (idx_row_col, 2 * nv + idx_row_col)), shape=(nv, 3 * nv), dtype=np.int64)

    # faces along x direction (faces with negative indices)
    idx_col = idx[:-1, :, :].flatten()
    idx_row = idx[+1:, :, :].flatten()
    data = -np.ones((nx - 1) * ny * nz, dtype=np.int64)
    A_vox += sps.csc_matrix((data, (idx_row, 0 * nv + idx_col)), shape=(nv, 3 * nv), dtype=np.int64)

    # faces along y direction (faces with negative indices)
    idx_col = idx[:, :-1, :].flatten()
    idx_row = idx[:, +1:, :].flatten()
    data = -np.ones(nx * (ny - 1) * nz, dtype=np.int64)
    A_vox += sps.csc_matrix((data, (idx_row, 1 * nv + idx_col)), shape=(nv, 3 * nv), dtype=np.int64)

    # faces along z direction (faces with negative indices)
    idx_col = idx[:, :, :-1].flatten()
    idx_row = idx[:, :, +1:].flatten()
    data = -np.ones(nx * ny * (nz - 1), dtype=np.int64)
    A_vox += sps.csc_matrix((data, (idx_row, 2 * nv + idx_col)), shape=(nv, 3 * nv), dtype=np.int64)

    return A_vox
