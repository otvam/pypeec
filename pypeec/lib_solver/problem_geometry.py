"""
Different functions for handling the specified geometry (materials and sources).
Create and manage the indices of the different voxels and faces.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import numpy as np
from pypeec.lib_utils import timelogger
from pypeec import config

# get a logger
LOGGER = timelogger.get_logger("PROBLEM")

# get config
NP_TYPES = config.NP_TYPES


def get_material_indices(material_idx, material_type_ref):
    """
    Get the indices of the voxels for a given material type.
    """

    # array for the indices
    idx_v = np.array([], dtype=NP_TYPES.INT)

    # populate the arrays
    for tag, dat_tmp in material_idx.items():
        # get the data
        material_type = dat_tmp["material_type"]
        idx = dat_tmp["idx"]

        # assign the indices
        if material_type == material_type_ref:
            idx_v = np.append(idx_v, idx)

    return idx_v


def get_source_indices(source_idx, source_type_ref):
    """
    Get the indices of the source voxels for a given source type.
    """

    # array for the source indices
    idx_src = np.array([], dtype=NP_TYPES.INT)

    # populate the arrays with the current sources
    for tag, dat_tmp in source_idx.items():
        # get the data
        source_type = dat_tmp["source_type"]
        idx = dat_tmp["idx"]

        # assign the indices
        if source_type == source_type_ref:
            idx_src = np.append(idx_src, idx)

    return idx_src


def get_reduce_matrix(pts_vox, A_vox, idx_v):
    """
    Reduce the matrices to the non-empty voxels and compute face indices.

    The voxel structure has the following size: (nx, ny, nz).
    The problem contains n_v non-empty voxels and n_f internal faces.
    At the input, the complete coordinate matrix is provided: (nx*ny*nz, 3).
    At the input, the complete incidence matrix is provided: (nx*ny*nz, 3*nx*ny*nz).
    At the output, the reduced coordinate matrix is provided: (n_v, 3).
    At the output, the reduced incidence matrix is provided: (n_v, n_f).
    The indices of the internal faces are also computed.
    """

    # reduce the size of the voxel coordinate amtrix
    pts_net = pts_vox[idx_v, :]

    # reduce the size of the incidence matrix (only the non-empty voxels)
    A_net = A_vox[idx_v, :]

    # indices of the all the internal faces (global face indices, 0:3*n)
    idx_f = np.sum(np.abs(A_net), axis=0) == 2
    idx_f = np.flatnonzero(idx_f).astype(NP_TYPES.INT)

    # reduce the size of the incidence matrix (only the internal faces)
    A_net = A_net[:, idx_f]

    # cast to float
    A_net = A_net.astype(NP_TYPES.FLOAT)

    return pts_net, A_net, idx_f


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
    LOGGER.debug("problem size: n_voxel = %d" % n_voxel)
    LOGGER.debug("problem size: n_face = %d" % n_face)
    LOGGER.debug("problem size: n_voxel_electric = %d" % n_voxel_electric)
    LOGGER.debug("problem size: n_voxel_magnetic = %d" % n_voxel_magnetic)
    LOGGER.debug("problem size: n_face_electric = %d" % n_face_electric)
    LOGGER.debug("problem size: n_face_magnetic = %d" % n_face_magnetic)
    LOGGER.debug("problem size: n_src_current = %d" % n_src_current)
    LOGGER.debug("problem size: n_src_voltage = %d" % n_src_voltage)
    LOGGER.debug("problem size: ratio_voxel = %.3e" % ratio_voxel)
    LOGGER.debug("problem size: ratio_face = %.3e" % ratio_face)

    return problem_status
