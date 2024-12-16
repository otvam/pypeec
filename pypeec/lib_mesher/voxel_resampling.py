"""
Different functions for resampling a voxel structure.
Refine and reduce a voxel structure and update the voxel indices.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import scilogger
import numpy as np

# get a logger
LOGGER = scilogger.get_logger(__name__, "pypeec")


def _get_idx_resample_tensor(resampling_factor, idx_n, idx_r, idx):
    """
    Transform original voxel indices into resampled voxel indices.

    The input indices are linear indices.
    The output indices are tensor indices.
    """

    # extract the resampling
    (rx, ry, rz) = resampling_factor

    # get the provided indices (tensor indices instead of linear indices)
    idx_n_x = idx_n[:, 0][idx]
    idx_n_y = idx_n[:, 1][idx]
    idx_n_z = idx_n[:, 2][idx]

    # get the tensor indices of a single resampled voxel
    idx_r_x = idx_r[:, [0]]
    idx_r_y = idx_r[:, [1]]
    idx_r_z = idx_r[:, [2]]

    # get the global indices
    idx_x = rx * idx_n_x + idx_r_x
    idx_y = ry * idx_n_y + idx_r_y
    idx_z = rz * idx_n_z + idx_r_z

    return idx_x, idx_y, idx_z


def _get_idx_reduce_tensor(idx_n, idx_min, idx):
    """
    Transform original voxel indices into reduced tensor indices.

    The input indices are linear indices.
    The output indices are tensor indices.
    """

    # get the provided indices (tensor indices instead of linear indices)
    idx_x = idx_n[:, 0][idx]
    idx_y = idx_n[:, 1][idx]
    idx_z = idx_n[:, 2][idx]

    # reduce the size of the voxel structure
    idx_x -= idx_min[0]
    idx_y -= idx_min[1]
    idx_z -= idx_min[2]

    return idx_x, idx_y, idx_z


def _get_idx_linear(n, idx_x, idx_y, idx_z):
    """
    Transform tensor indices into linear indices.
    """

    # extract the voxel data
    (nx, ny, nz) = n

    # convert tensor indices into linear indices
    idx_out = idx_x + nx * idx_y + nx * ny * idx_z
    idx_out = idx_out.flatten()

    return idx_out


def _get_original_grid(n):
    """
    Get the indices of the voxels composing the original grid.
    The first resampled voxel has the index zero.
    """

    # extract the voxel data
    (nx, ny, nz) = n

    # get total size
    nv = np.prod(n)

    # get the indices of the original grid
    idx_all = np.arange(nv, dtype=np.int64)
    (idx_n_x, idx_n_y, idx_n_z) = np.unravel_index(idx_all, (nx, ny, nz), order="F")

    # assemble the coordinate array
    idx_n = np.stack((idx_n_x, idx_n_y, idx_n_z), axis=1)

    return idx_n


def _get_resampled_grid(resampling_factor):
    """
    Get the indices of the different sub-voxels composing a single original voxel (after resampling).
    The first resampled sub-voxel has the index zero.
    """

    # extract the resampling resampling_factors
    (rx, ry, rz) = resampling_factor

    # get the number of resampled voxels per original voxel
    rv = rx * ry * rz

    # get the indices of a single resampled voxel
    idx_all = np.arange(rv, dtype=np.int64)
    (idx_r_x, idx_r_y, idx_r_z) = np.unravel_index(idx_all, (rx, ry, rz), order="F")

    # assemble the coordinate array
    idx_r = np.stack((idx_r_x, idx_r_y, idx_r_z), axis=1)

    return idx_r


def _get_grid_bounds(idx_n, domain_def):
    """
    Get the bounds of the tensor structures.
    The bounds are meant with respect to the non-empty voxels.
    """

    # init the array
    idx_lin = np.empty(0, dtype=np.int64)

    # find the indices
    for idx in domain_def.values():
        idx_lin = np.append(idx_lin, idx)

    # get the tensor indices
    idx_grid = idx_n[idx_lin]

    # get the bounds
    idx_min = np.min(idx_grid, axis=0)
    idx_max = np.max(idx_grid, axis=0)

    return idx_min, idx_max


def _get_reduce_indices(n, idx_n, idx_min, domain_def):
    """
    Update the indices of the domains such that they match the reduced structure.
    """

    for tag, idx in domain_def.items():
        # update the old voxel indices into the new tensor indices
        (idx_x, idx_y, idx_z) = _get_idx_reduce_tensor(idx_n, idx_min, idx)

        # transform the tensor indices into linear indices
        idx = _get_idx_linear(n, idx_x, idx_y, idx_z)

        # assign the new indices
        domain_def[tag] = idx

    return domain_def


def _get_update_indices(n, resampling_factor, idx_n, idx_r, domain_def):
    """
    Update the indices of the domains such that they match the resampled structure.
    """

    for tag, idx in domain_def.items():
        # update the old voxel indices into the new tensor indices
        (idx_x, idx_y, idx_z) = _get_idx_resample_tensor(resampling_factor, idx_n, idx_r, idx)

        # transform the tensor indices into linear indices
        idx = _get_idx_linear(n, idx_x, idx_y, idx_z)

        # assign the new indices
        domain_def[tag] = idx

    return domain_def


def _get_update_size(n, d, resampling_factor):
    """
    Update the number of voxels and the dimension of the voxels for the given resampling.
    """

    # extract the voxel data
    (nx, ny, nz) = n
    (dx, dy, dz) = d

    # extract the resampling resampling_factors
    (rx, ry, rz) = resampling_factor

    # update the number of voxels
    n = [nx * rx, ny * ry, nz * rz]

    # update the dimension of the voxels
    d = [dx / rx, dy / ry, dz / rz]

    return n, d


def _get_reduce(n, d, c, domain_def):
    """
    Remove unused voxels from a voxel structure.
    """

    # get the original grid indices
    idx_n = _get_original_grid(n)

    # update the indices of the problem
    (idx_min, idx_max) = _get_grid_bounds(idx_n, domain_def)

    # get the center shift
    n_diff = (idx_min + idx_max + 1 - n) / 2
    c += n_diff * d

    # get the new voxel number
    n = idx_max - idx_min + 1

    # cast to list
    n = n.tolist()
    c = c.tolist()

    # update the indices of the problem
    domain_def = _get_reduce_indices(n, idx_n, idx_min, domain_def)

    return n, c, domain_def


def _get_resample(n, d, domain_def, resampling_factor):
    """
    Resampling of a voxel structure (increases the number of voxels).
    """

    # get the original grid indices
    idx_n = _get_original_grid(n)

    # get the indices of a single resampled voxel
    idx_r = _get_resampled_grid(resampling_factor)

    # update the voxel number and size
    (n, d) = _get_update_size(n, d, resampling_factor)

    # update the indices of the problem
    domain_def = _get_update_indices(n, resampling_factor, idx_n, idx_r, domain_def)

    return n, d, domain_def


def get_resampling(n, d, c, domain_def, data_resampling):
    """
    Remesh of a voxel structure (remove unused voxels and resampling).
    """

    # extract the data
    use_reduce = data_resampling["use_reduce"]
    use_resample = data_resampling["use_resample"]
    resampling_factor = data_resampling["resampling_factor"]

    # display number of voxels
    LOGGER.debug("use_reduce = %s" % use_reduce)
    LOGGER.debug("use_resample = %s" % use_resample)
    LOGGER.debug("original number = %d" % np.prod(n))

    # remove unused voxels
    if use_reduce:
        (n, c, domain_def) = _get_reduce(n, d, c, domain_def)

    # resampling of the voxel structure
    if use_resample:
        (n, d, domain_def) = _get_resample(n, d, domain_def, resampling_factor)

    # voxel structure size
    s = tuple(x * y for x, y in zip(n, d, strict=True))

    # display number of voxels
    LOGGER.debug("final number = %d" % np.prod(n))

    return n, d, c, s, domain_def
