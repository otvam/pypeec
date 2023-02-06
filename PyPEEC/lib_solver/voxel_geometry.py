"""
Different functions for dealing the voxel data.
Compute the voxel coordinates and the incidence matrix.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np
import scipy.sparse as sps


def get_voxel_point(n, d, c):
    """
    Get the coordinate of the different voxels.
    The first voxel center is at the specified origin coordinate.

    The voxel structure has the following size: (nx, ny, nz).
    The array has the following dimension: (nx*ny*nz, 3).
    """

    # extract the voxel data
    (nx, ny, nz) = n
    (dx, dy, dz) = d
    (cx, cy, cz) = c

    # voxel index array
    idx_x = np.arange(nx, dtype=np.int64)
    idx_y = np.arange(ny, dtype=np.int64)
    idx_z = np.arange(nz, dtype=np.int64)
    (idx_x, idx_y, idx_z) = np.meshgrid(idx_x, idx_y, idx_z, indexing="ij")

    # origin coordinate
    ox = cx-(nx*dx)/2
    oy = cy-(ny*dy)/2
    oz = cz-(nz*dz)/2

    # voxel coordinate vector
    x = ox+dx/2+dx*np.arange(nx, dtype=np.float64)
    y = oy+dy/2+dy*np.arange(ny, dtype=np.float64)
    z = oz+dz/2+dz*np.arange(nz, dtype=np.float64)

    # assemble the coordinate array
    x = x[idx_x].flatten(order="F")
    y = y[idx_y].flatten(order="F")
    z = z[idx_z].flatten(order="F")

    # assemble the coordinate array
    voxel_point = np.stack((x, y, z), axis=1)

    return voxel_point


def get_incidence_matrix(n):
    """
    Get the incidence matrix of the voxel structure.
    This matrix describes the relation between the voxels and the faces.

    The voxel structure has the following size: (nx, ny, nz).
    The matrix has the following dimension: (nx*ny*nz, 3*nx*ny*nz).
    """

    # extract the voxel data
    (nx, ny, nz) = n
    nv = nx*ny*nz

    # voxel index array
    x = np.arange(nx, dtype=np.int64)
    y = np.arange(ny, dtype=np.int64)
    z = np.arange(nz, dtype=np.int64)
    (idx_x, idx_y, idx_z) = np.meshgrid(x, y, z, indexing="ij")

    # voxel index number
    idx = idx_x+idx_y*nx+idx_z*nx*ny

    # create the sparse matrix
    A_incidence = sps.csc_matrix((nv, 3*nv), dtype=np.int64)

    # assign the diagonal, each voxel is connected to three faces with positive indices
    data = np.ones(nv)
    idx_row_col = np.arange(nv)
    A_incidence += sps.csc_matrix((data, (idx_row_col, 0*nv+idx_row_col)), shape=(nv, 3*nv), dtype=np.int64)
    A_incidence += sps.csc_matrix((data, (idx_row_col, 1*nv+idx_row_col)), shape=(nv, 3*nv), dtype=np.int64)
    A_incidence += sps.csc_matrix((data, (idx_row_col, 2*nv+idx_row_col)), shape=(nv, 3*nv), dtype=np.int64)

    # faces along x direction (faces with negative indices)
    idx_col = idx[0:-1, :, :].flatten()
    idx_row = idx[1:, :, :].flatten()
    data = -np.ones((nx-1)*ny*nz, dtype=np.int64)
    A_incidence += sps.csc_matrix((data, (idx_row, 0*nv+idx_col)), shape=(nv, 3*nv), dtype=np.int64)

    # faces along y direction (faces with negative indices)
    idx_col = idx[:, 0:-1, :].flatten()
    idx_row = idx[:, 1:, :].flatten()
    data = -np.ones(nx*(ny-1)*nz, dtype=np.int64)
    A_incidence += sps.csc_matrix((data, (idx_row, 1*nv+idx_col)), shape=(nv, 3*nv), dtype=np.int64)

    # faces along z direction (faces with negative indices)
    idx_col = idx[:, :, 0:-1].flatten()
    idx_row = idx[:, :, 1:].flatten()
    data = -np.ones(nx*ny*(nz-1), dtype=np.int64)
    A_incidence += sps.csc_matrix((data, (idx_row, 2*nv+idx_col)), shape=(nv, 3*nv), dtype=np.int64)

    return A_incidence
