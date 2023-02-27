"""
Different functions for handling the specified geometry (materials and sources).
Create and manage the indices of the different voxels and faces.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import numpy as np
from pypeec.lib_utils import timelogger

# get a logger
logger = timelogger.get_logger("PROBLEM")


def get_material_geometry(material_idx, extract_type):
    """
    Get the indices of the material voxels and the corresponding resistivities.
    For electric materials, the provided resistivity is used.
    For magnetic materials, an equivalent resistivity is computed from the susceptibility.
    """

    # array for the indices and resistivities
    idx_v = np.array([], dtype=np.int_)
    rho_v = np.array([], dtype=np.complex_)

    # populate the arrays
    for tag, dat_tmp in material_idx.items():
        # get the data
        material_type = dat_tmp["material_type"]
        idx = dat_tmp["idx"]

        # the current source value is set such that the sum across all voxels is equal to the specified value
        if (len(idx) > 0) and (material_type == extract_type):
            # find the resistivity
            if material_type == "electric":
                rho = dat_tmp["rho"]
            elif material_type == "magnetic":
                # get the magnetic susceptibility
                chi = dat_tmp["chi"]

                # vacuum permeability
                mu = 4*np.pi*1e-7

                # equivalent magnetic resistivity
                rho = 1/(mu*chi)
            else:
                raise ValueError("invalid material type")

            # append the indices and resistivities
            idx_v = np.append(idx_v, idx)
            rho_v = np.append(rho_v, np.full(len(idx), rho))

    return idx_v, rho_v


def get_source_geometry(source_idx, extract_type):
    """
    Get the indices of the source voxels and the corresponding source parameters.
    """

    # array for the current source indices and source values
    idx_src = np.array([], dtype=np.int_)
    value_src = np.array([], dtype=np.complex_)
    element_src = np.array([], dtype=np.complex_)

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
                Y = dat_tmp["Y"]
                value_src = np.append(value_src, np.full(len(idx), I/len(idx)))
                element_src = np.append(element_src, np.full(len(idx), Y/len(idx)))
            elif source_type == "voltage":
                V = dat_tmp["V"]
                Z = dat_tmp["Z"]
                value_src = np.append(value_src, np.full(len(idx), V))
                element_src = np.append(element_src, np.full(len(idx), Z*len(idx)))
            else:
                raise ValueError("invalid source type")

    return idx_src, value_src, element_src


def get_incidence_matrix(A_vox, idx_v):
    """
    Reduce the incidence matrix to the non-empty voxels and compute face indices.

    The voxel structure has the following size: (nx, ny, nz).
    The problem contains n_v non-empty voxels and n_f internal faces.
    At the input, the complete incidence matrix is provided: (nx*ny*nz, 3*nx*ny*nz).
    At the output, the reduced incidence matrix is provided: (n_v, n_f).
    The indices of the internal faces is also computed.
    """

    # reduce the size of the incidence matrix (only the non-empty voxels)
    A_net = A_vox[idx_v, :]

    # indices of the all the internal faces (global face indices, 0:3*n)
    idx_f = np.sum(np.abs(A_net), axis=0) == 2
    idx_f = np.flatnonzero(idx_f)

    # reduce the size of the incidence matrix (only the internal faces)
    A_net = A_net[:, idx_f]

    return A_net, idx_f


def get_status(n, idx_vc, idx_vm, idx_fc, idx_fm, idx_src_c, idx_src_v):
    """
    Get a dict summarizing the problem size.
    Total number of voxels, number of non-empty voxels, number of faces, and number of sources.
    """

    # extract the voxel data
    (nx, ny, nz) = n

    # count
    n_voxel = nx*ny*nz
    n_face = 3*nx*ny*nz
    n_voxel_electric = len(idx_vc)
    n_voxel_magnetic = len(idx_vm)
    n_face_electric = len(idx_fc)
    n_face_magnetic = len(idx_fm)
    n_src_current = len(idx_src_c)
    n_src_voltage = len(idx_src_v)

    # fraction of voxels
    ratio_voxel = (n_voxel_electric+n_voxel_magnetic)/n_voxel
    ratio_face = (n_face_electric+n_face_magnetic)/n_face

    # assign data
    problem_status = {
        "n_voxel": n_voxel,
        "n_face": n_face,
        "n_voxel_electric": n_voxel_electric,
        "n_voxel_magnetic": n_voxel_magnetic,
        "n_face_electric": n_face_electric,
        "n_face_magnetic": n_face_magnetic,
        "n_src_current": n_src_current,
        "n_src_voltage": n_src_voltage,
        "ratio_voxel": ratio_voxel,
        "ratio_face": ratio_face,
    }

    # display status
    logger.debug("problem size: n_voxel = %d" % n_voxel)
    logger.debug("problem size: n_face = %d" % n_face)
    logger.debug("problem size: n_voxel_electric = %d" % n_voxel_electric)
    logger.debug("problem size: n_voxel_magnetic = %d" % n_voxel_magnetic)
    logger.debug("problem size: n_face_electric = %d" % n_face_electric)
    logger.debug("problem size: n_face_magnetic = %d" % n_face_magnetic)
    logger.debug("problem size: n_src_current = %d" % n_src_current)
    logger.debug("problem size: n_src_voltage = %d" % n_src_voltage)
    logger.debug("problem size: ratio_voxel = %.3e" % ratio_voxel)
    logger.debug("problem size: ratio_face = %.3e" % ratio_face)

    return problem_status
