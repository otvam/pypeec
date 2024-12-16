"""
Different functions for handling the problem values:
    - materials properties (electric and magnetic materials)
    - source values and internal impedance/admittance
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import scilogger
import numpy as np
import scipy.constants as cst

# get a logger
LOGGER = scilogger.get_logger(__name__, "pypeec")


def _get_material_field(val_dict):
    """
    Cast and check the material vectors.
    If the variable is a scalar, cast to an array.
    If the variable is an array, check the length.
    """

    # extract the data
    orientation_type = val_dict["orientation_type"]
    material_type = val_dict["material_type"]
    var_type = val_dict["var_type"]
    idx = val_dict["idx"]

    # find required fields
    if material_type == "electric":
        tag_list = ["rho_re", "rho_im"]
    elif material_type == "magnetic":
        tag_list = ["chi_re", "chi_im"]
    elif material_type == "electromagnetic":
        tag_list = ["rho_re", "rho_im", "chi_re", "chi_im"]
    else:
        raise ValueError("invalid material type")

    for tag in tag_list:
        # extract
        val = val_dict[tag]

        # cast
        if var_type == "lumped" and orientation_type is None:
            val = np.full(len(idx), val, dtype=np.float64)
        elif var_type == "lumped" and orientation_type == "isotropic":
            val = np.full((len(idx), 3), val, dtype=np.float64)
        elif var_type == "lumped" and orientation_type == "anisotropic":
            val = np.array(val, dtype=np.float64)
            val = np.tile(val, (len(idx), 1))
        elif var_type == "distributed" and orientation_type is None:
            val = np.array(val, dtype=np.float64)
        elif var_type == "distributed" and orientation_type == "isotropic":
            val = np.array(val, dtype=np.float64)
            val = np.tile(val, (3, 1)).transpose()
        elif var_type == "distributed" and orientation_type == "anisotropic":
            val = np.array(val, dtype=np.float64)

        # check
        if not (val.shape == (len(idx), 3)):
            raise RuntimeError("vector length does not match the number of voxels")

        # update
        val_dict[tag] = val

    return val_dict


def _get_source_field(val_dict):
    """
    Cast and check the source vectors.
    If the variable is a scalar, cast to an array.
    If the variable is an array, check the length.
    """

    # extract the data
    source_type = val_dict["source_type"]
    var_type = val_dict["var_type"]
    idx = val_dict["idx"]

    # find required fields
    if source_type == "current":
        tag_list = ["I_re", "I_im", "Y_re", "Y_im"]
    elif source_type == "voltage":
        tag_list = ["V_re", "V_im", "Z_re", "Z_im"]
    else:
        raise ValueError("invalid material type")

    for tag in tag_list:
        # extract
        val = val_dict[tag]

        # cast
        if var_type == "lumped":
            val = np.full(len(idx), val, dtype=np.float64)
        elif var_type == "distributed":
            val = np.array(val, dtype=np.float64)

        # check
        if not (len(val) == len(idx)):
            raise RuntimeError("vector length does not match the number of voxels")

        # update
        val_dict[tag] = val

    return val_dict


def _merge_val_idx(dict_val, dict_idx):
    """
    Merge the value and the index dicts.
    Check that the name are compatible.
    """

    dict_all = {}
    for tag in dict_idx:
        # check domain
        if tag not in dict_val:
            raise RuntimeError("invalid domain: name not found: %s" % tag)

        # merge
        dict_all[tag] = {**dict_val[tag], **dict_idx[tag]}

    return dict_all


def get_material_value(material_val, material_idx):
    """
    Check the size of the material values.
    Convert the values to arrays.
    """

    # mege data
    material_all = _merge_val_idx(material_val, material_idx)

    # reshape data
    for tag, material_all_tmp in material_all.items():
        material_all[tag] = _get_material_field(material_all_tmp)

    return material_all


def get_source_value(source_val, source_idx):
    """
    Check the size of the source values.
    Convert the values to arrays.
    """

    # mege data
    source_all = _merge_val_idx(source_val, source_idx)

    # reshape data
    for tag, source_all_tmp in source_all.items():
        source_all[tag] = _get_source_field(source_all_tmp)

    return source_all


def get_material_vector(material_all):
    """
    Get the material parameters for the different material types.
    """

    # array for the resistivities
    rho_vc = np.empty((0, 3), dtype=np.complex128)
    rho_vm = np.empty((0, 3), dtype=np.complex128)

    # populate the arrays
    for material_all_tmp in material_all.values():
        # extract the data
        material_type = material_all_tmp["material_type"]
        idx = material_all_tmp["idx"]

        # get the resistivities for the electric materials
        if material_type in ["electric", "electromagnetic"]:
            # assemble
            rho_re = material_all_tmp["rho_re"]
            rho_im = material_all_tmp["rho_im"]
            rho = rho_re + 1j * rho_im

            # check size
            if len(rho) != len(idx):
                raise RuntimeError("invalid material parameters")

            # append the resistivities
            rho_vc = np.concatenate((rho_vc, rho))

        # get the resistivities for the magnetic materials
        if material_type in ["magnetic", "electromagnetic"]:
            # assemble
            chi_re = material_all_tmp["chi_re"]
            chi_im = material_all_tmp["chi_im"]
            chi = chi_re - 1j * chi_im
            rho = 1 / (cst.mu_0 * chi)

            # check size
            if len(rho) != len(idx):
                raise RuntimeError("invalid material parameters")

            # append the resistivities
            rho_vm = np.concatenate((rho_vm, rho))

    return rho_vc, rho_vm


def get_source_vector(source_all, source_type_ref):
    """
    Get the source parameters for a given source type.
    """

    # array for the source indices
    value_src = np.empty(0, dtype=np.complex128)
    element_src = np.empty(0, dtype=np.complex128)

    # populate the arrays with the current sources
    for source_all_tmp in source_all.values():
        # extract the data
        source_type = source_all_tmp["source_type"]
        var_type = source_all_tmp["var_type"]
        idx = source_all_tmp["idx"]

        # get the values and admittances/impedances for the source
        if source_type == "current":
            # extract the data
            I_re = source_all_tmp["I_re"]
            I_im = source_all_tmp["I_im"]
            Y_re = source_all_tmp["Y_re"]
            Y_im = source_all_tmp["Y_im"]
            value = I_re + 1j * I_im
            element = Y_re + 1j * Y_im
        elif source_type == "voltage":
            # extract the data
            V_re = source_all_tmp["V_re"]
            V_im = source_all_tmp["V_im"]
            Z_re = source_all_tmp["Z_re"]
            Z_im = source_all_tmp["Z_im"]
            value = V_re + 1j * V_im
            element = Z_re + 1j * Z_im
        else:
            raise ValueError("invalid source type")

        # scale the lumped parameters for current source
        if (source_type == "current") and (var_type == "lumped"):
            value = value / len(idx)
            element = element / len(idx)

        # scale the lumped parameters for voltage source
        if (source_type == "voltage") and (var_type == "lumped"):
            element = element * len(idx)

        # check size
        if len(value) != len(idx):
            raise RuntimeError("invalid source parameters")
        if len(element) != len(idx):
            raise RuntimeError("invalid source parameters")

        # append the source values and admittances/impedances
        if source_type == source_type_ref:
            value_src = np.concatenate((value_src, value))
            element_src = np.concatenate((element_src, element))

    return value_src, element_src


def get_resistance_vector(n, d, A_net, idx_f, rho_v):
    """
    Extract the resistance vector of the system (diagonal of the resistance matrix).

    The problem contains n_f internal faces.
    The resistance vector has the following length: n_f.
    """

    # extract the voxel data
    (dx, dy, dz) = d

    # get total size
    nv = np.prod(n)

    # get the resistivity of the faces (average between voxels)
    rho = 0.5 * rho_v.transpose() * np.abs(A_net)

    # get the direction of the faces (x, y, z)
    idx_fx = np.isin(idx_f, np.arange(0 * nv, 1 * nv, dtype=np.int64))
    idx_fy = np.isin(idx_f, np.arange(1 * nv, 2 * nv, dtype=np.int64))
    idx_fz = np.isin(idx_f, np.arange(2 * nv, 3 * nv, dtype=np.int64))

    # resistance vector (different directions)
    R = np.zeros(len(idx_f), dtype=np.complex128)
    R[idx_fx] = (dx / (dy * dz)) * rho[0, idx_fx]
    R[idx_fy] = (dy / (dx * dz)) * rho[1, idx_fy]
    R[idx_fz] = (dz / (dx * dy)) * rho[2, idx_fz]

    return R
