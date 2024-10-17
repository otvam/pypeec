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
            val = np.full(len(idx), val, dtype=np.float_)
        elif var_type == "lumped" and orientation_type == "isotropic":
            val = np.full((len(idx), 3), val, dtype=np.float_)
        elif var_type == "lumped" and orientation_type == "anisotropic":
            val = np.array(val, dtype=np.float_)
            val = np.tile(val, (len(idx), 1))
        elif var_type == "distributed" and orientation_type is None:
            val = np.array(val, dtype=np.float_)
        elif var_type == "distributed" and orientation_type == "isotropic":
            val = np.array(val, dtype=np.float_)
            val = np.tile(val, (3, 1)).transpose()
        elif var_type == "distributed" and orientation_type == "anisotropic":
            val = np.array(val, dtype=np.float_)

        # check
        if not (val.shape == (len(idx), 3)):
            raise RuntimeError("vector length does not match the number of voxels")

        # update
        val_dict[tag] = val

    return val_dict


def _get_source_field(val_dict, idx, var_type):
    """
    Cast and check the source vectors.
    If the variable is a scalar, cast to an array.
    If the variable is an array, check the length.
    """

    for tag, val in val_dict.items():
        # cast
        if var_type == "lumped":
            val = np.full(len(idx), val, dtype=np.float_)
        elif var_type == "distributed":
            val = np.array(val, dtype=np.float_)

        # check
        if not (len(val) == len(idx)):
            raise RuntimeError("vector length does not match the number of voxels")

        # update
        val_dict[tag] = val

    return val_dict


def get_material_value(material_val, material_idx):
    """
    Check the size of the material values.
    Convert the values to arrays.
    """

    # mege data
    material_all = {}
    for tag in material_idx:
        material_all[tag] = {**material_val[tag], **material_idx[tag]}

    # reshape data
    for tag, material_all_tmp in material_all.items():
        # check type
        material_all[tag] = _get_material_field(material_all_tmp)

    return material_all


def get_source_value(source_val, source_idx):
    """
    Check the size of the source values.
    Convert the values to arrays.
    """

    for tag, source_val_tmp in source_val.items():
        # extract the data
        var_type = source_idx[tag]["var_type"]
        idx = source_idx[tag]["idx"]

        # check type
        source_val[tag] = _get_source_field(source_val_tmp, idx, var_type)

    return source_val


def get_material_vector(material_all):
    """
    Get the material parameters for the different material types.
    """

    # array for the resistivities
    rho_vc = np.empty((0, 3), dtype=np.complex_)
    rho_vm = np.empty((0, 3), dtype=np.complex_)

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
            rho = rho_re+1j*rho_im

            # append the resistivities
            rho_vc = np.concatenate((rho_vc, rho))

        # get the resistivities for the magnetic materials
        if material_type in ["magnetic", "electromagnetic"]:
            # assemble
            chi_re = material_all_tmp["chi_re"]
            chi_im = material_all_tmp["chi_im"]
            chi = chi_re-1j*chi_im
            rho = 1/(cst.mu_0*chi)

            # append the resistivities
            rho_vm = np.concatenate((rho_vm, rho))

    return rho_vc, rho_vm


def get_source_all(source_val, source_idx):
    """
    Merge the different source structures.
    """

    # init combined array
    source_all = {}

    # populate the arrays with the current sources
    for tag in source_idx:
        # extract the data
        source_type = source_idx[tag]["source_type"]
        var_type = source_idx[tag]["var_type"]
        idx_src = source_idx[tag]["idx_src"]
        idx_vc = source_idx[tag]["idx_vc"]
        idx = source_idx[tag]["idx"]

        # get the values and admittances/impedances for the source
        if source_type == "current":
            # extract the data
            I_re = source_val[tag]["I_re"]
            I_im = source_val[tag]["I_im"]
            Y_re = source_val[tag]["Y_re"]
            Y_im = source_val[tag]["Y_im"]
            value = I_re+1j*I_im
            element = Y_re+1j*Y_im

            # scale the lumped parameters
            if var_type == "lumped":
                value_all = value/len(idx)
                element_all = element/len(idx)
            elif var_type == "distributed":
                value_all = value
                element_all = element
            else:
                raise ValueError("invalid variable type")
        elif source_type == "voltage":
            # extract the data
            V_re = source_val[tag]["V_re"]
            V_im = source_val[tag]["V_im"]
            Z_re = source_val[tag]["Z_re"]
            Z_im = source_val[tag]["Z_im"]
            value = V_re+1j*V_im
            element = Z_re+1j*Z_im

            # scale the lumped parameters
            if var_type == "lumped":
                value_all = value
                element_all = element*len(idx)
            elif var_type == "distributed":
                value_all = value
                element_all = element
            else:
                raise ValueError("invalid variable type")
        else:
            raise ValueError("invalid source type")

        # assign merged data
        source_all[tag] = {
            "source_type": source_type,
            "var_type": var_type,
            "idx": idx,
            "idx_src": idx_src,
            "idx_vc": idx_vc,
            "value": value_all,
            "element": element_all,
        }

    return source_all


def get_source_vector(source_all, source_type_ref):
    """
    Get the source parameters for a given source type.
    """

    # array for the source indices
    value_src = np.empty(0, dtype=np.complex_)
    element_src = np.empty(0, dtype=np.complex_)

    # populate the arrays with the current sources
    for tag, source_idx_tmp in source_all.items():
        # extract the data
        source_type = source_idx_tmp["source_type"]
        value = source_idx_tmp["value"]
        element = source_idx_tmp["element"]
        idx = source_idx_tmp["idx"]

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
    (nx, ny, nz) = n
    (dx, dy, dz) = d
    nv = nx*ny*nz

    # get the resistivity of the faces (average between voxels)
    rho = 0.5*rho_v.transpose()*np.abs(A_net)

    # get the direction of the faces (x, y, z)
    idx_fx = np.in1d(idx_f, np.arange(0*nv, 1*nv, dtype=np.int_))
    idx_fy = np.in1d(idx_f, np.arange(1*nv, 2*nv, dtype=np.int_))
    idx_fz = np.in1d(idx_f, np.arange(2*nv, 3*nv, dtype=np.int_))

    # resistance vector (different directions)
    R = np.zeros(len(idx_f), dtype=np.complex_)
    R[idx_fx] = (dx/(dy*dz))*rho[0, idx_fx]
    R[idx_fy] = (dy/(dx*dz))*rho[1, idx_fy]
    R[idx_fz] = (dz/(dx*dy))*rho[2, idx_fz]

    return R
