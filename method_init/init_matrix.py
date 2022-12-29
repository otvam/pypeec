"""
Different functions for dealing the voxel data.
These functions are used during the init phase of the FFT-PEEC method.
"""

import numpy as np
import scipy.sparse as sps

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2022 - Dartmouth College"


def get_voxel_coordinate(d, n):
    """
    Get the coordinate of the voxels.
    The first voxel is at the origin.
    The array has the following dimension: (nx, ny, nz, 3).
    """

    # extract the voxel data
    (nx, ny, nz) = n
    (dx, dy, dz) = d

    # voxel index array
    x = np.arange(nx)
    y = np.arange(ny)
    z = np.arange(nz)
    (idx_x, idx_y, idx_z) = np.meshgrid(x, y, z, indexing='ij')

    # voxel coordinate vector
    x = dx*np.arange(nx)
    y = dy*np.arange(ny)
    z = dz*np.arange(nz)

    # assemble the coordinate array
    xyz = np.stack((x[idx_x], y[idx_y], z[idx_z]), axis=3, dtype=np.float64)

    return xyz


def get_incidence_matrix(n):
    """
    Get the incidence matrix of the voxels.
    This matrix describes the relation between the voxels and the faces.
    The matrix has the following dimension: (nx*ny*nz, 3*nx*ny*nz).
    """

    # extract the voxel data
    (nx, ny, nz) = n
    n = nx*ny*nz

    # voxel index array
    x = np.arange(nx)
    y = np.arange(ny)
    z = np.arange(nz)
    (idx_x, idx_y, idx_z) = np.meshgrid(x, y, z, indexing='ij')

    # voxel index number
    idx = idx_x+idx_y*nx+idx_z*nx*ny

    # create the sparse matrix
    A_incidence = sps.csc_matrix((n, 3*n), dtype=np.int64)

    # assign the diagonal, each voxel is connected to three faces with positive indices
    data = np.ones(n)
    idx_row_col = np.arange(n)
    A_incidence += sps.csc_matrix((data, (idx_row_col, 0*n+idx_row_col)), shape=(n, 3*n), dtype=np.int64)
    A_incidence += sps.csc_matrix((data, (idx_row_col, 1*n+idx_row_col)), shape=(n, 3*n), dtype=np.int64)
    A_incidence += sps.csc_matrix((data, (idx_row_col, 2*n+idx_row_col)), shape=(n, 3*n), dtype=np.int64)

    # faces along x direction (faces with negative indices)
    idx_col = idx[0:-1, :, :].flatten()
    idx_row = idx[1:, :, :].flatten()
    data = -np.ones((nx-1)*ny*nz)
    A_incidence += sps.csc_matrix((data, (idx_row, 0*n+idx_col)), shape=(n, 3*n), dtype=np.int64)

    # faces along y direction (faces with negative indices)
    idx_col = idx[:, 0:-1, :].flatten()
    idx_row = idx[:, 1:, :].flatten()
    data = -np.ones(nx*(ny-1)*nz)
    A_incidence += sps.csc_matrix((data, (idx_row, 1*n+idx_col)), shape=(n, 3*n), dtype=np.int64)

    # faces along z direction (faces with negative indices)
    idx_col = idx[:, :, 0:-1].flatten()
    idx_row = idx[:, :, 1:].flatten()
    data = -np.ones(nx*ny*(nz-1))
    A_incidence += sps.csc_matrix((data, (idx_row, 2*n+idx_col)), shape=(n, 3*n), dtype=np.int64)

    return A_incidence
