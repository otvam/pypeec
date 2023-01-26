"""
Different functions for resampling a voxel structure.
Refine a voxel structure and update the voxel indices.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np


def _get_idx_resample_tensor(r, idx_n, idx_r, idx):
    """
    Transform linear indices (original voxels) into tensor indices (resample voxels).

    The linear indices are within the following range: 0:nx*ny*nz.
    The tensor indices are within the following range: (0:nx*rx, 0:ny*ry, 0:nz*rz).

    The length of the provided linear indices is n_idx.
    The number of sub-voxels per original voxel is rx*ry*rz.
    The computed tensor indices have the following dimension: (rx*ry*rz, n_idx).
    """

    # extract the voxel data
    (rx, ry, rz) = r

    # get the provided indices (tensor indices instead of linear indices)
    idx_n_x = idx_n[:, 0][idx]
    idx_n_y = idx_n[:, 1][idx]
    idx_n_z = idx_n[:, 2][idx]

    # get the tensor indices of a single resampled voxel
    idx_r_x = idx_r[:, [0]]
    idx_r_y = idx_r[:, [1]]
    idx_r_z = idx_r[:, [2]]

    # get the global indices
    idx_nr_x = rx*idx_n_x+idx_r_x
    idx_nr_y = ry*idx_n_y+idx_r_y
    idx_nr_z = rz*idx_n_z+idx_r_z

    return idx_nr_x, idx_nr_y, idx_nr_z


def _get_idx_resample_linear(n, r, idx_nr_x, idx_nr_y, idx_nr_z):
    """
    Transform tensor indices (resample voxels) into linear indices (resample voxels).

    The provided tensor indices have the following dimension: (rx*ry*rz, n_idx).
    The computed linear indices have the following dimension: rx*ry*rz*n_idx.
    """

    # extract the voxel data
    (rx, ry, rz) = r
    (nx, ny, nz) = n

    # convert tensor indices into linear indices
    idx_out = idx_nr_x+rx*nx*idx_nr_y+rx*nx*ry*ny*idx_nr_z
    idx_out = idx_out.flatten()

    return idx_out


def _get_original_grid(n):
    """
    Get the indices of the voxels composing the original grid.
    The first resampled voxel has the index zero.
    """

    # extract the voxel data
    (nx, ny, nz) = n
    n = nx*ny*nz

    # get the indices of the original grid
    (idx_n_x, idx_n_y, idx_n_z) = np.unravel_index(np.arange(n), (nx, ny, nz), order="F")

    # assemble the coordinate array
    idx_n = np.stack((idx_n_x, idx_n_y, idx_n_z), axis=1)

    return idx_n


def _get_resampled_voxel(resampling):
    """
    Get the indices of the different sub-voxels composing a single original voxel (after resampling).
    The first resampled sub-voxel has the index zero.
    """

    # extract the voxel data
    (rx, ry, rz) = resampling
    r = rx*ry*rz

    # get the indices of a single resampled voxel
    (idx_r_x, idx_r_y, idx_r_z) = np.unravel_index(np.arange(r), (rx, ry, rz), order="F")

    # assemble the coordinate array
    idx_r = np.stack((idx_r_x, idx_r_y, idx_r_z), axis=1)

    return idx_r


def _get_update_indices(n, r, idx_n, idx_r, domain_def):
    """
    Update the indices of the domains such that they match the resampled structure.
    """

    for tag, idx in domain_def.items():
        # update the old voxel indices into the new tensor indices
        (idx_nr_x, idx_nr_y, idx_nr_z) = _get_idx_resample_tensor(r, idx_n, idx_r, idx)

        # transform the tensor indices into linear indices
        idx = _get_idx_resample_linear(n, r, idx_nr_x, idx_nr_y, idx_nr_z)

        # assign the new indices
        domain_def[tag] = idx

    return domain_def


def _get_update_size(n, d, resampling):
    """
    Update the number of voxels and the dimension of the voxels for the given resampling.
    """

    # extract the voxel data
    (nx, ny, nz) = n
    (dx, dy, dz) = d
    (rx, ry, rz) = resampling

    # update the number of voxels
    n = [nx*rx, ny*ry, nz*rz]

    # update the dimension of the voxels
    d = [dx/rx, dy/ry, dz/rz]

    return n, d


def get_remesh(n, d, domain_def, resampling):
    """
    Resampling of a voxel structure (increases the number of voxels).
    """

    # get the original grid indices
    idx_n = _get_original_grid(n)

    # get the indices of a single resampled voxel
    idx_r = _get_resampled_voxel(resampling)

    # update the indices of the problem
    domain_def = _get_update_indices(n, resampling, idx_n, idx_r, domain_def)

    # update the voxel number and size
    (n, d) = _get_update_size(n, d, resampling)

    return n, d, domain_def




