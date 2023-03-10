"""
Different functions for handling the specified geometry (materials and sources).
Create and manage the indices of the different voxels and faces.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import numpy as np
from pypeec.lib_utils import timelogger
from pypeec.lib_utils import config

# get config
NP_TYPES = config.NP_TYPES

# get a logger
logger = timelogger.get_logger("PROBLEM")


def get_material_magnetic(material_idx):
    """
    Get the indices of the magnetic voxels and the corresponding resistivities.
    An equivalent resistivity is computed from the susceptibility.
    """

    # array for the indices and resistivities
    idx_v = np.array([], dtype=NP_TYPES.INT)
    rho_v = np.array([], dtype=NP_TYPES.COMPLEX)

    # populate the arrays
    for tag, dat_tmp in material_idx.items():
        if dat_tmp["material_type"] == "magnetic":
            # get the magnetic susceptibility
            chi_re = dat_tmp["chi_re"]
            chi_im = dat_tmp["chi_im"]
            idx = dat_tmp["idx"]

            # vacuum permeability
            mu = 4*np.pi*1e-7

            # equivalent magnetic resistivity
            chi = chi_re-1j*chi_im
            rho = 1/(mu*chi)

            # append the indices and resistivities
            idx_v = np.append(idx_v, idx)
            rho_v = np.append(rho_v, rho)

    return idx_v, rho_v


def get_material_electric(material_idx):
    """
    Get the indices of the electric voxels and the corresponding resistivities.
    """

    # array for the indices and resistivities
    idx_v = np.array([], dtype=NP_TYPES.INT)
    rho_v = np.array([], dtype=NP_TYPES.COMPLEX)

    # populate the arrays
    for tag, dat_tmp in material_idx.items():
        if dat_tmp["material_type"] == "electric":
            # find the resistivity
            idx = dat_tmp["idx"]
            rho = dat_tmp["rho"]

            # append the indices and resistivities
            idx_v = np.append(idx_v, idx)
            rho_v = np.append(rho_v, rho)

    return idx_v, rho_v


def get_source_current(source_idx):
    """
    Get the indices of the current source voxels and the corresponding parameters.
    """

    # array for the current source indices and source values
    idx_src = np.array([], dtype=NP_TYPES.INT)
    value_src = np.array([], dtype=NP_TYPES.COMPLEX)
    element_src = np.array([], dtype=NP_TYPES.COMPLEX)

    # populate the arrays with the current sources
    for tag, dat_tmp in source_idx.items():
        if dat_tmp["source_type"] == "current":
            # extract data
            I_tmp = dat_tmp["I_re"]+1j*dat_tmp["I_im"]
            Y_tmp = dat_tmp["Y_re"]+1j*dat_tmp["Y_im"]
            var_type = dat_tmp["var_type"]
            idx = dat_tmp["idx"]

            # compute the source for each voxel
            if var_type == "lumped":
                value_tmp = I_tmp/len(idx)
                element_tmp = Y_tmp/len(idx)
            elif var_type == "distributed":
                value_tmp = I_tmp
                element_tmp = Y_tmp
            else:
                raise ValueError("invalid material type")

            # append the source
            idx_src = np.append(idx_src, idx)
            value_src = np.append(value_src, value_tmp)
            element_src = np.append(element_src, element_tmp)

    return idx_src, value_src, element_src


def get_source_voltage(source_idx):
    """
    Get the indices of the voltage source voxels and the corresponding parameters.
    """

    # array for the current source indices and source values
    idx_src = np.array([], dtype=NP_TYPES.INT)
    value_src = np.array([], dtype=NP_TYPES.COMPLEX)
    element_src = np.array([], dtype=NP_TYPES.COMPLEX)

    # populate the arrays with the current sources
    for tag, dat_tmp in source_idx.items():
        if dat_tmp["source_type"] == "voltage":
            # extract data
            V_tmp = dat_tmp["V_re"]+1j*dat_tmp["V_im"]
            Z_tmp = dat_tmp["Z_re"]+1j*dat_tmp["Z_im"]
            var_type = dat_tmp["var_type"]
            idx = dat_tmp["idx"]

            # compute the source for each voxel
            if var_type == "lumped":
                value_tmp = V_tmp
                element_tmp = Z_tmp*len(idx)
            elif var_type == "distributed":
                value_tmp = V_tmp
                element_tmp = Z_tmp
            else:
                raise ValueError("invalid material type")

            # append the source
            idx_src = np.append(idx_src, idx)
            value_src = np.append(value_src, value_tmp)
            element_src = np.append(element_src, element_tmp)

    return idx_src, value_src, element_src


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
