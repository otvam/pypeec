"""
Different functions for handling the specified geometry (conductors and sources).
Create and manage the indices of the different voxels and faces.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np
from PyPEEC.lib_utils import timelogger

# get a logger
logger = timelogger.get_logger("PROBLEM")


def get_material_geometry(material_idx, extract_type):
    """
    Get the indices of the material voxels and the corresponding resistivities.
    """

    # array for the indices and resistivities
    idx_v = np.array([], dtype=np.int64)
    rho_v = np.array([], dtype=np.float64)

    # populate the arrays
    for tag, dat_tmp in material_idx.items():
        # get the data
        material_type = dat_tmp["material_type"]
        idx = dat_tmp["idx"]

        # the current source value is set such that the sum across all voxels is equal to the specified value
        if (len(idx) > 0) and (material_type == extract_type):
            # append the indices
            idx_v = np.append(idx_v, idx)

            # find the resistivity
            if material_type == "conductor":
                rho = dat_tmp["rho"]
                rho_v = np.append(rho_v, np.full(len(idx), rho))
            elif material_type == "magnetic":
                chi = dat_tmp["chi"]
                rho_v = np.append(rho_v, np.full(len(idx), 1/chi))
            else:
                raise ValueError("invalid material type")

    return idx_v, rho_v


def get_source_geometry(source_idx, extract_type):
    """
    Get the indices of the source voxels and the corresponding source excitations.
    """

    # array for the current source indices and source values
    idx_src = np.array([], dtype=np.int64)
    value_src = np.array([], dtype=np.complex128)
    element_src = np.array([], dtype=np.float64)

    # populate the arrays with the current sources
    for tag, dat_tmp in source_idx.items():
        # get the data
        source_type = dat_tmp["source_type"]
        idx = dat_tmp["idx"]

        # the current source value is set such that the sum across all voxels is equal to the specified value
        if (len(idx) > 0) and (source_type == extract_type):
            # append the indices
            idx_src = np.append(idx_src, idx)

            # find the source value
            if source_type == "current":
                I = dat_tmp["I"]
                G = dat_tmp["G"]
                value_src = np.append(value_src, np.full(len(idx), I/len(idx)))
                element_src = np.append(element_src, np.full(len(idx), G/len(idx)))
            elif source_type == "voltage":
                V = dat_tmp["V"]
                R = dat_tmp["R"]
                value_src = np.append(value_src, np.full(len(idx), V))
                element_src = np.append(element_src, np.full(len(idx), R*len(idx)))
            else:
                raise ValueError("invalid source type")

    return idx_src, value_src, element_src


def get_incidence_matrix(A_inc, idx_v):
    """
    Reduce the incidence matrix to the non-empty voxels and compute face indices.

    The voxel structure has the following size: (nx, ny, nz).
    The problem contains n_v non-empty voxels and n_f internal faces.
    At the input, the complete incidence matrix is provided: (nx*ny*nz, 3*nx*ny*nz).
    At the output, the reduced incidence matrix is provided: (n_v, n_f).
    The indices of the internal faces is also computed.
    """

    # reduce the size of the incidence matrix (only the non-empty voxels)
    A_red = A_inc[idx_v, :]

    # indices of the all the internal faces (global face indices, 0:3*n)
    idx_f = np.sum(np.abs(A_red), axis=0) == 2
    idx_f = np.flatnonzero(idx_f)

    # reduce the size of the incidence matrix (only the internal faces)
    A_red = A_red[:, idx_f]

    return A_red, idx_f


def get_status(n, idx_vc, idx_vm, idx_fc, idx_fm, idx_src_c, idx_src_v):
    """
    Get a dict summarizing the problem size.
    Total number of voxels, number of non-empty voxels, number of faces, and number of sources.
    """

    # extract the voxel data
    (nx, ny, nz) = n

    # count
    n_total = nx*ny*nz
    n_voxel_conductor = len(idx_vc)
    n_voxel_magnetic = len(idx_vm)
    n_face_conductor = len(idx_fc)
    n_face_magnetic = len(idx_fm)
    n_src_current = len(idx_src_c)
    n_src_voltage = len(idx_src_v)

    # fraction of voxels
    ratio_voxel = (n_voxel_conductor+n_voxel_magnetic)/n_total
    ratio_face = (n_face_conductor+n_face_magnetic)/(3*n_total)

    # assign data
    problem_status = {
        "n_total": n_total,
        "n_voxel_conductor": n_voxel_conductor,
        "n_voxel_magnetic": n_voxel_magnetic,
        "n_face_conductor": n_face_conductor,
        "n_face_magnetic": n_face_magnetic,
        "n_src_current": n_src_current,
        "n_src_voltage": n_src_voltage,
        "ratio_voxel": ratio_voxel,
        "ratio_face": ratio_face,
    }

    # display status
    logger.info("problem size: n_total = %d" % n_total)
    logger.info("problem size: n_voxel_conductor = %d" % n_voxel_conductor)
    logger.info("problem size: n_voxel_magnetic = %d" % n_voxel_magnetic)
    logger.info("problem size: n_face_conductor = %d" % n_face_conductor)
    logger.info("problem size: n_face_magnetic = %d" % n_face_magnetic)
    logger.info("problem size: n_src_current = %d" % n_src_current)
    logger.info("problem size: n_src_voltage = %d" % n_src_voltage)
    logger.info("problem size: ratio_voxel = %.3e" % ratio_voxel)
    logger.info("problem size: ratio_face = %.3e" % ratio_face)

    return problem_status
