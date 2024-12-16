"""
Module for handling voxel indices (1D and 3D indices):
    - the 1D indices are also called linear indices
    - the 3D indices are also called tensor indices
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import numpy as np


def get_idx_linear(n, idx_tensor):
    """
    Transform tensor indices into linear indices.
    """

    # extract the voxel data
    (nx, ny, nz) = n

    # cast to array
    idx_tensor = np.array(idx_tensor, dtype=np.int64)

    # extract indices
    idx_x = idx_tensor[:, 0]
    idx_y = idx_tensor[:, 1]
    idx_z = idx_tensor[:, 2]

    # check bounds
    if not (np.all(idx_x >= 0) and np.all(idx_x < nx)):
        raise ValueError("invalid index range (x coordinate)")
    if not (np.all(idx_y >= 0) and np.all(idx_y < nx)):
        raise ValueError("invalid index range (y coordinate)")
    if not (np.all(idx_z >= 0) and np.all(idx_z < nz)):
        raise ValueError("invalid index range (z coordinate)")

    # convert tensor indices into linear indices
    idx_linear = idx_x + nx * idx_y + nx * ny * idx_z

    return idx_linear


def get_idx_tensor(n, idx_linear):
    """
    Transform linear indices into tensor indices.
    """

    # extract the voxel data
    (nx, ny, nz) = n

    # get total size
    nv = np.prod(n)

    # cast to array
    idx_linear = np.array(idx_linear, dtype=np.int64)

    # check bounds
    if not (np.all(idx_linear >= 0) and np.all(idx_linear < nv)):
        raise ValueError("invalid index range")

    # convert linear indices into tensor indices
    (idx_x, idx_y, idx_z) = np.unravel_index(idx_linear, (nx, ny, nz), order="F")

    # assemble the coordinate array
    idx_tensor = np.stack((idx_x, idx_y, idx_z), axis=1)

    return idx_tensor
