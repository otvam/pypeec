"""
Different functions for handling the specified geometry (materials and sources).
Create and manage the indices of the different voxels and faces.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import scilogger
import numpy as np

# get a logger
LOGGER = scilogger.get_logger(__name__, "pypeec")


def _get_domain_indices(domain_list, domain_def):
    """
    Get indices from a list of domain names.
    """

    idx_all = np.empty(0, dtype=np.int64)
    for tag in domain_list:
        # check domain
        if tag not in domain_def:
            raise RuntimeError("invalid domain: name not found: %s" % tag)

        # add indices
        idx_tmp = np.array(domain_def[tag], dtype=np.int64)
        idx_all = np.append(idx_all, idx_tmp)

    return idx_all


def _check_indices(idx_vc, idx_src_c, idx_src_v):
    """
    Check that the material and source indices are valid.
    The indices should be unique and compatible with the voxel size.
    The source indices should be included in the electric indices.
    Check that there is at least one source per connected electrical.
    """

    # check the indices
    if len(idx_vc) == 0:
        raise RuntimeError("the geometry does not include any electric voxel")

    if (len(idx_src_c) == 0) and (len(idx_src_v) == 0):
        raise RuntimeError("the geometry does not include any source voxel")

    # check that the terminal indices are electric indices
    if not np.all(np.isin(idx_src_c, idx_vc)):
        raise RuntimeError("current source voxels should overlap with electric voxels")
    if not np.all(np.isin(idx_src_v, idx_vc)):
        raise RuntimeError("voltage source voxels should overlap with electric voxels")


def _check_source_graph(idx_vc, idx_src_c, idx_src_v, graph_def):
    """
    Check that there is at least one source per connected component.
    A connected components without a source would lead to a singular problem.
    """

    for idx_graph in graph_def:
        has_electric = len(np.intersect1d(idx_graph, idx_vc)) > 0
        has_current_source = len(np.intersect1d(idx_graph, idx_src_c)) > 0
        has_voltage_source = len(np.intersect1d(idx_graph, idx_src_v)) > 0

        if has_electric:
            if not (has_current_source or has_voltage_source):
                raise RuntimeError("electric components should include at least one source")


def get_problem_type(idx_vc, idx_vm, idx_src_c, idx_src_v, graph_def):
    """
    Check the validity of the problem.
    Detect if magnetic material are present.
    """

    # check voxel indices
    _check_indices(idx_vc, idx_src_c, idx_src_v)
    _check_source_graph(idx_vc, idx_src_c, idx_src_v, graph_def)

    # detect the existence of magnetic domains
    has_magnetic = len(idx_vm) > 0

    return has_magnetic


def get_material_idx(material_def, domain_def):
    """
    Get the indices of the material.
    Create a new dict with the indices in place of the domain names.
    Split the electric and magnetic materials.
    """

    # init
    material_idx = {}
    idx_vc = np.empty(0, dtype=np.int64)
    idx_vm = np.empty(0, dtype=np.int64)

    for tag, material_def_tmp in material_def.items():
        # extract the data
        var_type = material_def_tmp["var_type"]
        material_type = material_def_tmp["material_type"]
        orientation_type = material_def_tmp["orientation_type"]
        domain_list = material_def_tmp["domain_list"]

        # get indices
        idx = _get_domain_indices(domain_list, domain_def)

        # assign the indices
        if material_type == "electric":
            idx_vc = np.append(idx_vc, idx)
        elif material_type == "magnetic":
            idx_vm = np.append(idx_vm, idx)
        elif material_type == "electromagnetic":
            idx_vc = np.append(idx_vc, idx)
            idx_vm = np.append(idx_vm, idx)
        else:
            raise ValueError("invalid material type")

        # assign the material
        material_idx[tag] = {
            "idx": idx,
            "var_type": var_type,
            "material_type": material_type,
            "orientation_type": orientation_type,
        }

    return idx_vc, idx_vm, material_idx


def get_source_idx(source_def, domain_def):
    """
    Get the indices of the sources.
    Create a new dict with the indices in place of the domain names.
    """

    # init
    source_idx = {}
    idx_src_c = np.empty(0, dtype=np.int64)
    idx_src_v = np.empty(0, dtype=np.int64)

    for tag, source_def_tmp in source_def.items():
        # extract the data
        var_type = source_def_tmp["var_type"]
        source_type = source_def_tmp["source_type"]
        domain_list = source_def_tmp["domain_list"]

        # get indices
        idx = _get_domain_indices(domain_list, domain_def)

        # assign the indices
        if source_type == "current":
            idx_src_c = np.append(idx_src_c, idx)
        if source_type == "voltage":
            idx_src_v = np.append(idx_src_v, idx)

        # get the source value
        source_idx[tag] = {
            "idx": idx,
            "source_type": source_type,
            "var_type": var_type,
        }

    return idx_src_c, idx_src_v, source_idx


def get_material_pos(material_idx, idx_vc, idx_vm):
    """
    Get the indices of the electric and magnetic materials.
    Convert from voxel indices to solver indices.
    """

    # parse the material domains
    for tag, material_idx_tmp in material_idx.items():
        # extract the data
        idx = material_idx_tmp["idx"]

        # get the position of the material domain
        idx_vc_tmp = np.isin(idx_vc, idx)
        idx_vm_tmp = np.isin(idx_vm, idx)

        # find indices
        idx_vc_tmp = np.flatnonzero(idx_vc_tmp)
        idx_vm_tmp = np.flatnonzero(idx_vm_tmp)

        # assign the losses
        material_idx[tag]["idx_vc"] = idx_vc_tmp
        material_idx[tag]["idx_vm"] = idx_vm_tmp

    return material_idx


def get_source_pos(source_idx, idx_vc, idx_src_c, idx_src_v):
    """
    Get the indices of the source terminal voltages and currents.
    Convert from voxel indices to solver indices.
    """

    # assemble indices
    idx_src = np.concatenate((idx_src_c, idx_src_v))

    # parse the source terminals
    for tag, source_idx_tmp in source_idx.items():
        # extract the data
        idx = source_idx_tmp["idx"]

        # get the position of the voltage terminals
        idx_vc_tmp = np.isin(idx_vc, idx)
        idx_src_tmp = np.isin(idx_src, idx)

        # find indices
        idx_vc_tmp = np.flatnonzero(idx_vc_tmp)
        idx_src_tmp = np.flatnonzero(idx_src_tmp)

        # assign the current and voltage
        source_idx[tag]["idx_vc"] = idx_vc_tmp
        source_idx[tag]["idx_src"] = idx_src_tmp

    return source_idx


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
    idx_f = np.flatnonzero(idx_f)

    # reduce the size of the incidence matrix (only the internal faces)
    A_net = A_net[:, idx_f]

    return pts_net, A_net, idx_f


def get_status(n, idx_vc, idx_vm, idx_fc, idx_fm, idx_src_c, idx_src_v):
    """
    Get a dict summarizing the problem size.
    Total number of voxels, number of non-empty voxels, number of faces, and number of sources.
    """

    # extract the voxel data
    (nx, ny, nz) = n

    # count
    n_voxel_total = nx * ny * nz
    n_face_total = 3 * nx * ny * nz
    n_voxel_electric = len(idx_vc)
    n_voxel_magnetic = len(idx_vm)
    n_face_electric = len(idx_fc)
    n_face_magnetic = len(idx_fm)
    n_src_current = len(idx_src_c)
    n_src_voltage = len(idx_src_v)

    # fraction of voxels
    n_voxel_used = n_voxel_electric + n_voxel_magnetic
    n_face_used = n_face_electric + n_face_magnetic
    ratio_voxel = n_voxel_used / n_voxel_total
    ratio_face = n_face_used / n_face_total

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
