"""
Different functions for handling the specified geometry (conductors and sources).
Create and manage the indices of the different voxels and faces.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np
from main import logging_utils

# get a logger
logger = logging_utils.get_logger("problem")


def get_conductor_geometry(conductor):
    """
    Get the indices of the conducting voxels and the corresponding resistivities.
    """

    # array for the indices and resistivities
    idx_v = np.array([], dtype=np.int64)
    rho_v = np.array([], dtype=np.float64)

    # populate the arrays
    for tag, dat_tmp in conductor.items():
        # get the data_output
        idx = dat_tmp["idx"]
        rho = dat_tmp["rho"]

        # append (all voxels in a group have the same resistivities)
        idx_v = np.append(idx_v, np.array(idx))
        rho_v = np.append(rho_v, np.full(len(idx), rho))

    return idx_v, rho_v


def get_source_geometry(source):
    """
    Get the indices of the source voxels and the corresponding source excitations.
    """

    # array for the current source indices and source values
    idx_src_c = np.array([], dtype=np.int64)
    val_src_c = np.array([], dtype=np.complex128)

    # array for the voltage source indices and source values
    idx_src_v = np.array([], dtype=np.int64)
    val_src_v = np.array([], dtype=np.complex128)

    # populate the arrays with the current sources
    for tag, dat_tmp in source.items():
        # get the data_output
        source_type = dat_tmp["source_type"]
        idx = dat_tmp["idx"]
        value = dat_tmp["value"]

        # append the source
        if len(idx) > 0:
            if source_type == "current":
                # the current source value is set such that the sum across all voxels is equal to the specified value
                idx_src_c = np.append(idx_src_c, np.array(idx))
                val_src_c = np.append(val_src_c, np.full(len(idx), value / len(idx)))
            elif source_type == "voltage":
                # the voltage source value is set to the specified value for all the voxels
                idx_src_v = np.append(idx_src_v, np.array(idx))
                val_src_v = np.append(val_src_v, np.full(len(idx), value))
            else:
                raise ValueError("invalid terminal type")

    return idx_src_c, val_src_c, idx_src_v, val_src_v


def get_source_index(n, idx_v, idx_src_c, idx_src_v):
    """
    Compute the local indices for the sources.
    At the input, the indices are relative to the complete voxel structures.
    At the output, the indices are relative to the non-empty voxels (conductors).
    """

    # extract the voxel data_output
    (nx, ny, nz) = n
    n_v = len(idx_v)
    n = nx*ny*nz

    # get the local indices for the current source
    idx_tmp = np.zeros(n, dtype=np.int64)
    idx_tmp[idx_v] = np.arange(n_v, dtype=np.int64)
    idx_src_c_local = idx_tmp[idx_src_c]

    # get the local indices for the voltage source
    idx_tmp = np.zeros(n, dtype=np.int64)
    idx_tmp[idx_v] = np.arange(n_v, dtype=np.int64)
    idx_src_v_local = idx_tmp[idx_src_v]

    # get the voxel as a boolean array
    idx_voxel = np.zeros(n, dtype=bool)
    idx_voxel[idx_v] = True

    return idx_voxel, idx_src_c_local, idx_src_v_local


def get_incidence_matrix(n, A_incidence, idx_v):
    """
    Reduce the incidence matrix to the non-empty voxels and compute face indices.
    The problem contains n_v non-empty voxels and n_f internal faces.
    At the input, the complete incidence matrix is provided: (nx*ny*nz, 3*nx*ny*nz).
    At the output, the reduced incidence matrix is provided: (n_v, n_f).
    The indices of the internal faces is also computed.
    """

    # extract the voxel data_output
    (nx, ny, nz) = n
    n = nx*ny*nz

    # reduce the size of the incidence matrix (only the non-empty voxels)
    A_reduced = A_incidence[idx_v, :]

    # indices of the x-oriented faces (local face indices, 0:n)
    idx_f_x = np.sum(np.abs(A_reduced[:, 0:n]), axis=0) == 2
    idx_f_x = np.flatnonzero(idx_f_x)

    # indices of the y-oriented faces (local face indices, 0:n)
    idx_f_y = np.sum(np.abs(A_reduced[:, n:2*n]), axis=0) == 2
    idx_f_y = np.flatnonzero(idx_f_y)

    # indices of the z-oriented faces (local face indices, 0:n)
    idx_f_z = np.sum(np.abs(A_reduced[:, 2*n:3*n]), axis=0) == 2
    idx_f_z = np.flatnonzero(idx_f_z)

    # indices of the all the internal faces (global face indices, 0:3*n)
    idx_f = np.sum(np.abs(A_reduced), axis=0) == 2
    idx_f = np.flatnonzero(idx_f)

    # reduce the size of the incidence matrix (only the internal faces)
    A_reduced = A_reduced[:, idx_f]

    return A_reduced, idx_f_x, idx_f_y, idx_f_z, idx_f


def get_status(n, idx_v, idx_f, idx_src_c, idx_src_v):
    """
    Get a dict summarizing the problem size.
    Total number of voxels, number of non-empty voxels, number of faces, and number of sources.
    """

    # extract the voxel data_output
    (nx, ny, nz) = n

    # count
    n_total = nx*ny*nz
    n_conductor = len(idx_v)
    n_faces = len(idx_f)
    n_src = len(idx_src_c)+len(idx_src_v)

    # fraction of voxels
    ratio_conductor = n_conductor/n_total
    ratio_src = n_src/n_total

    # assign data_output
    problem_status = {
        "n_total": n_total,
        "n_conductor": n_conductor,
        "n_faces": n_faces,
        "n_src": n_src,
        "ratio_conductor": ratio_conductor,
        "ratio_src": ratio_src,
    }

    # display status
    logger.info("problem size: n_total = %d" % n_total)
    logger.info("problem size: n_conductor = %d" % n_conductor)
    logger.info("problem size: n_faces = %d" % n_faces)
    logger.info("problem size: n_src = %d" % n_src)
    logger.info("problem size: ratio_conductor = %.3e" % ratio_conductor)
    logger.info("problem size: ratio_src = %.3e" % ratio_src)

    return problem_status
