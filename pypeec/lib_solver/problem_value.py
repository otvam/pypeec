"""
Different functions for handling the problem values:
    - materials properties (electric and magnetic materials)
    - source values and internal impedance/admittance
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import numpy as np
import scipy.constants as cst
from pypeec import log

# get a logger
LOGGER = log.get_logger(__name__, "pypeec")


def get_material_vector(material_val, material_idx):
    """
    Get the material parameters for the different material types.
    """

    # array for the resistivities
    rho_vc = np.empty((0, 3), dtype=np.complex_)
    rho_vm = np.empty((0, 3), dtype=np.complex_)

    # populate the arrays
    for tag, material_idx_tmp in material_idx.items():
        # extract the data
        material_type = material_idx_tmp["material_type"]
        idx = material_idx_tmp["idx"]

        # get the resistivities for the electric materials
        if material_type in ["electric", "electromagnetic"]:
            # assemble
            rho_re = material_val[tag]["rho_re"]
            rho_im = material_val[tag]["rho_im"]
            rho = rho_re+1j*rho_im

            # check size
            if len(rho) != len(idx):
                raise RuntimeError("invalid source")

            # append the resistivities
            rho_vc = np.concatenate((rho_vc, rho))

        # get the resistivities for the magnetic materials
        if material_type in ["magnetic", "electromagnetic"]:
            # assemble
            chi_re = material_val[tag]["chi_re"]
            chi_im = material_val[tag]["chi_im"]
            chi = chi_re-1j*chi_im
            rho = 1/(cst.mu_0*chi)

            # check size
            if len(rho) != len(idx):
                raise RuntimeError("invalid material parameters")

            # append the resistivities
            rho_vm = np.concatenate((rho_vm, rho))

    return rho_vc, rho_vm


def get_source_all(source_val, source_pos, source_idx):
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
        idx = source_idx[tag]["idx"]

        # extract the data
        idx_src = source_pos[tag]["idx_src"]
        idx_vc = source_pos[tag]["idx_vc"]

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
