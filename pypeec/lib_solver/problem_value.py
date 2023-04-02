"""
Different functions for handling the problem values:
    - materials properties (electric and magnetic materials)
    - source values and internal impedance/admittance
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


def get_material_values(material_val, material_idx, material_type_ref):
    """
    Get the material parameters for a given material type.
    """

    # array for the resistivities
    rho_v = np.array([], dtype=NP_TYPES.COMPLEX)

    # populate the arrays
    for tag, dat_tmp in material_idx.items():
        # get the data
        material_type = dat_tmp["material_type"]
        idx = dat_tmp["idx"]

        # vacuum permeability
        mu = 4 * np.pi * 1e-7

        # get the resistivities for the material
        if material_type == "electric":
            rho_re = material_val[tag]["rho_re"]
            rho_im = material_val[tag]["rho_im"]
            rho = rho_re+1j*rho_im
        elif material_type == "magnetic":
            chi_re = material_val[tag]["chi_re"]
            chi_im = material_val[tag]["chi_im"]
            chi = chi_re-1j*chi_im
            rho = 1/(mu*chi)
        else:
            raise ValueError("invalid material type")

        # compute
        if len(rho) != len(idx):
            raise RuntimeError("invalid source")

        # append the resistivities
        if material_type == material_type_ref:
            rho_v = np.append(rho_v, rho)

    return rho_v


def get_source_values(source_val, source_idx, source_type_ref):
    """
    Get the source parameters for a given source type.
    """

    # array for the source indices
    value_src = np.array([], dtype=NP_TYPES.COMPLEX)
    element_src = np.array([], dtype=NP_TYPES.COMPLEX)

    # populate the arrays with the current sources
    for tag, dat_tmp in source_idx.items():
        # get the data
        source_type = dat_tmp["source_type"]
        var_type = dat_tmp["var_type"]
        idx = dat_tmp["idx"]

        # get the values and admittances/impedances for the source
        if source_type == "current":
            # extract data
            I_re = source_val[tag]["I_re"]
            I_im = source_val[tag]["I_im"]
            Y_re = source_val[tag]["Y_re"]
            Y_im = source_val[tag]["Y_im"]
            value = I_re+1j*I_im
            element = Y_re+1j*Y_im

            # compute the source for each voxel
            if var_type == "lumped":
                value = value/len(idx)
                element = element/len(idx)
            elif var_type == "distributed":
                pass
            else:
                raise ValueError("invalid variable type")
        elif source_type == "voltage":
            # extract data
            V_re = source_val[tag]["V_re"]
            V_im = source_val[tag]["V_im"]
            Z_re = source_val[tag]["Z_re"]
            Z_im = source_val[tag]["Z_im"]
            value = V_re+1j*V_im
            element = Z_re+1j*Z_im

            # compute the source for each voxel
            if var_type == "lumped":
                value = value*1
                element = element*len(idx)
            elif var_type == "distributed":
                pass
            else:
                raise ValueError("invalid variable type")
        else:
            raise ValueError("invalid material type")

        # append the source values and admittances/impedances
        if source_type == source_type_ref:
            value_src = np.append(value_src, value)
            element_src = np.append(element_src, element)

    return value_src, element_src


def get_value(value_idx):
    """
    Get the frequency, the material parameters, and the source values.
    """

    freq = value_idx["freq"]
    material_val = value_idx["material_val"]
    source_val = value_idx["source_val"]

    return freq, material_val, source_val
