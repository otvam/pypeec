"""
Different functions for handling the specified geometry (materials and sources).
Create and manage the indices of the different voxels and faces.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import numpy as np
from pypeec import log
from pypeec import config

# get a logger
LOGGER = log.get_logger("PROBLEM")

# get config
NP_TYPES = config.NP_TYPES


def get_material_indices(material_idx, material_type_ref):
    """
    Get the indices of the voxels for a given material type.
    """

    # array for the indices
    idx_v = np.array([], dtype=NP_TYPES.INT)

    # populate the arrays
    for tag, material_idx_tmp in material_idx.items():
        # extract the data
        material_type = material_idx_tmp["material_type"]
        idx = material_idx_tmp["idx"]

        # assign the indices
        if material_type == material_type_ref:
            idx_v = np.append(idx_v, idx)

    return idx_v


def get_material_pos(material_idx, idx_vc, idx_vm):
    """
    Get the indices of the electric and magnetic materials.
    Convert from voxel indices to solver indices.
    """

    # init material dict
    material_pos = {}

    # parse the material domains
    for tag, material_idx_tmp in material_idx.items():
        # extract the data
        idx = material_idx_tmp["idx"]

        # get the position of the material domain
        idx_vc_tmp = np.in1d(idx_vc, idx)
        idx_vm_tmp = np.in1d(idx_vm, idx)

        # find indices
        idx_vc_tmp = np.flatnonzero(idx_vc_tmp)
        idx_vm_tmp = np.flatnonzero(idx_vm_tmp)

        # assign the losses
        material_pos[tag] = {"idx_vc": idx_vc_tmp, "idx_vm": idx_vm_tmp}

    return material_pos


def get_source_indices(source_idx, source_type_ref):
    """
    Get the indices of the source voxels for a given source type.
    """

    # array for the source indices
    idx_src = np.array([], dtype=NP_TYPES.INT)

    # populate the arrays with the current sources
    for tag, source_idx_tmp in source_idx.items():
        # extract the data
        source_type = source_idx_tmp["source_type"]
        idx = source_idx_tmp["idx"]

        # assign the indices
        if source_type == source_type_ref:
            idx_src = np.append(idx_src, idx)

    return idx_src


def get_source_pos(source_idx, idx_vc, idx_src_c, idx_src_v):
    """
    Get the indices of the source terminal voltages and currents.
    Convert from voxel indices to solver indices.
    """

    # init source dict
    source_pos = {}

    # assemble indices
    idx_src = np.concatenate((idx_src_c, idx_src_v))

    # parse the source terminals
    for tag, source_idx_tmp in source_idx.items():
        # extract the data
        idx = source_idx_tmp["idx"]

        # get the position of the voltage terminals
        idx_vc_tmp = np.in1d(idx_vc, idx)
        idx_src_tmp = np.in1d(idx_src, idx)

        # find indices
        idx_vc_tmp = np.flatnonzero(idx_vc_tmp)
        idx_src_tmp = np.flatnonzero(idx_src_tmp)

        # assign the current and voltage
        source_pos[tag] = {"idx_vc": idx_vc_tmp, "idx_src": idx_src_tmp}

    return source_pos


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
    n_voxel_total = nx*ny*nz
    n_face_total = 3*nx*ny*nz
    n_voxel_electric = len(idx_vc)
    n_voxel_magnetic = len(idx_vm)
    n_face_electric = len(idx_fc)
    n_face_magnetic = len(idx_fm)
    n_src_current = len(idx_src_c)
    n_src_voltage = len(idx_src_v)

    # fraction of voxels
    n_voxel_used = n_voxel_electric+n_voxel_magnetic
    n_face_used = n_face_electric+n_face_magnetic
    ratio_voxel = n_voxel_used/n_voxel_total
    ratio_face = n_face_used/n_face_total

    # assign data
    problem_status = {
        "n_voxel_total": n_voxel_total,
        "n_face_total": n_face_total,
        "n_voxel_used": n_voxel_used,
        "n_face_used": n_face_used,
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
    LOGGER.debug("n_voxel_total = %d" % n_voxel_total)
    LOGGER.debug("n_voxel_used = %d" % n_voxel_used)
    LOGGER.debug("n_face_total = %d" % n_face_total)
    LOGGER.debug("n_face_used = %d" % n_face_used)
    LOGGER.debug("n_voxel_electric = %d" % n_voxel_electric)
    LOGGER.debug("n_voxel_magnetic = %d" % n_voxel_magnetic)
    LOGGER.debug("n_face_electric = %d" % n_face_electric)
    LOGGER.debug("n_face_magnetic = %d" % n_face_magnetic)
    LOGGER.debug("n_src_current = %d" % n_src_current)
    LOGGER.debug("n_src_voltage = %d" % n_src_voltage)
    LOGGER.debug("ratio_voxel = %.2e" % ratio_voxel)
    LOGGER.debug("ratio_face = %.2e" % ratio_face)

    return problem_status
