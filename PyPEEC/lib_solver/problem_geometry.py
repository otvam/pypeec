"""
Different functions for handling the specified geometry (conductors and sources).
Create and manage the indices of the different voxels and faces.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np
from PyPEEC.lib_shared import logging_utils

# get a logger
logger = logging_utils.get_logger("problem")


def get_conductor_geometry(conductor_idx):
    """
    Get the indices of the conducting voxels and the corresponding resistivities.
    """

    # array for the indices and resistivities
    idx_v = np.array([], dtype=np.int64)
    rho_v = np.array([], dtype=np.float64)

    # populate the arrays
    for tag, dat_tmp in conductor_idx.items():
        # get the data
        idx = dat_tmp["idx"]
        rho = dat_tmp["rho"]

        # append (all voxels in a group have the same resistivities)
        idx_v = np.append(idx_v, np.array(idx))
        rho_v = np.append(rho_v, np.full(len(idx), rho))

    return idx_v, rho_v


def get_source_current_geometry(source_idx):
    """
    Get the indices of the source voxels and the corresponding source excitations.
    The current sources have internal admittances.
    """

    # array for the current source indices and source values
    idx_src_c = np.array([], dtype=np.int64)
    I_src_c = np.array([], dtype=np.complex128)
    G_src_c = np.array([], dtype=np.float64)

    # populate the arrays with the current sources
    for tag, dat_tmp in source_idx.items():
        # get the data
        source_type = dat_tmp["source_type"]
        idx = dat_tmp["idx"]

        # the current source value is set such that the sum across all voxels is equal to the specified value
        if (len(idx) > 0) and (source_type == "current"):
            # get the data
            I = dat_tmp["I"]
            G = dat_tmp["G"]

            # append the local current sources
            idx_src_c = np.append(idx_src_c, np.array(idx))
            I_src_c = np.append(I_src_c, np.full(len(idx), I/len(idx)))
            G_src_c = np.append(G_src_c, np.full(len(idx), G/len(idx)))

    return idx_src_c, I_src_c, G_src_c


def get_source_voltage_geometry(source_idx):
    """
    Get the indices of the source voxels and the corresponding source excitations.
    The voltage sources have internal resistances.
    """

    # array for the voltage source indices and source values
    idx_src_v = np.array([], dtype=np.int64)
    V_src_v = np.array([], dtype=np.complex128)
    R_src_v = np.array([], dtype=np.float64)

    # populate the arrays with the current sources
    for tag, dat_tmp in source_idx.items():
        # get the data
        source_type = dat_tmp["source_type"]
        idx = dat_tmp["idx"]

        # the voltage source value is set to the specified value for all the voxels
        if (len(idx) > 0) and (source_type == "voltage"):
            # get the data
            V = dat_tmp["V"]
            R = dat_tmp["R"]

            # append the local voltage sources
            idx_src_v = np.append(idx_src_v, np.array(idx))
            V_src_v = np.append(V_src_v, np.full(len(idx), V))
            R_src_v = np.append(R_src_v, np.full(len(idx), R*len(idx)))

    return idx_src_v, V_src_v, R_src_v


def get_incidence_matrix(n, A_incidence, idx_v):
    """
    Reduce the incidence matrix to the non-empty voxels and compute face indices.
    The problem contains n_v non-empty voxels and n_f internal faces.
    At the input, the complete incidence matrix is provided: (nx*ny*nz, 3*nx*ny*nz).
    At the output, the reduced incidence matrix is provided: (n_v, n_f).
    The indices of the internal faces is also computed.
    """

    # extract the voxel data
    (nx, ny, nz) = n
    n = nx*ny*nz

    # reduce the size of the incidence matrix (only the non-empty voxels)
    A_reduced = A_incidence[idx_v, :]

    # indices of the all the internal faces (global face indices, 0:3*n)
    idx_f = np.sum(np.abs(A_reduced), axis=0) == 2
    idx_f = np.flatnonzero(idx_f)

    # reduce the size of the incidence matrix (only the internal faces)
    A_reduced = A_reduced[:, idx_f]

    return A_reduced, idx_f


def get_status(n, idx_v, idx_f, idx_src_c, idx_src_v):
    """
    Get a dict summarizing the problem size.
    Total number of voxels, number of non-empty voxels, number of faces, and number of sources.
    """

    # extract the voxel data
    (nx, ny, nz) = n

    # count
    n_total = nx*ny*nz
    n_conductor = len(idx_v)
    n_faces = len(idx_f)
    n_src = len(idx_src_c)+len(idx_src_v)

    # fraction of voxels
    ratio_conductor = n_conductor/n_total
    ratio_src = n_src/n_total

    # assign data
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
