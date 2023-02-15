"""
Module for checking the solver problem data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np
from PyPEEC.lib_utils.error import CheckError


def _check_material_def(material_def):
    """
    Check that the material definition is valid.
    """

    # check type
    if not isinstance(material_def, dict):
        raise CheckError("material_def: material definition should be a dict")
    if not material_def:
        raise CheckError("material_def: material definition cannot be empty")

    # check value
    for tag, dat_tmp in material_def.items():
        # extract the data
        material_type = dat_tmp["material_type"]
        domain_list = dat_tmp["domain_list"]

        # check type
        if not isinstance(tag, str):
            raise CheckError("tag: material name should be a string")
        if not isinstance(material_type, str):
            raise CheckError("material_type: material type should be a string")
        if not isinstance(domain_list, list):
            raise CheckError("domain_list: domain definition a list")

        # check value
        if not (material_type in ["electric", "magnetic"]):
            raise CheckError("material_type: material type should be electric or magnetic")
        if not all(np.issubdtype(type(x), str) for x in domain_list):
            raise CheckError("domain_list: domain name should be composed of strings")

        # get the source value
        if material_type == "electric":
            rho = dat_tmp["rho"]
            if not np.issubdtype(type(rho), np.floating):
                raise CheckError("rho: material parameter should be a float")
            if not (rho > 0):
                raise CheckError("rho: material parameter should be greater than zero")
        elif material_type == "magnetic":
            chi_re = dat_tmp["chi_re"]
            chi_im = dat_tmp["chi_im"]
            if not np.issubdtype(type(chi_re), np.floating):
                raise CheckError("chi_re: material parameter should be a float")
            if not np.issubdtype(type(chi_im), np.floating):
                raise CheckError("chi_im: material parameter should be a float")
            if not (chi_re >= 0):
                raise CheckError("chi_re: material parameter should be greater than zero")
            if not (chi_im >= 0):
                raise CheckError("chi_im: material parameter should be greater than zero")
        else:
            raise CheckError("invalid material type")


def _check_source_def(source_def):
    """
    Check that the source definition is valid.
    """

    # check type
    if not isinstance(source_def, dict):
        raise CheckError("source_def: source definition should be a dict")
    if not source_def:
        raise CheckError("source_def: source definition cannot be empty")

    # check value
    for tag, dat_tmp in source_def.items():
        # extract the data
        source_type = dat_tmp["source_type"]
        domain_list = dat_tmp["domain_list"]

        # check type
        if not isinstance(tag, str):
            raise CheckError("tag: source name should be a string")
        if not isinstance(source_type, str):
            raise CheckError("source_type: source type should be a string")
        if not isinstance(domain_list, list):
            raise CheckError("domain_list: domain definition a list")

        # check value
        if not (source_type in ["current", "voltage"]):
            raise CheckError("source_type: source type should be voltage or current")
        if not all(np.issubdtype(type(x), str) for x in domain_list):
            raise CheckError("domain_list: domain name should be composed of strings")

        # get the source value
        if source_type == "current":
            value = dat_tmp["I_re"]+1j*dat_tmp["I_im"]
            element = dat_tmp["Y_re"]+1j*dat_tmp["Y_im"]
        elif source_type == "voltage":
            value = dat_tmp["V_re"]+1j*dat_tmp["V_im"]
            element = dat_tmp["Z_re"]+1j*dat_tmp["Z_im"]
        else:
            raise CheckError("invalid source type")

        # check the source type
        if not np.issubdtype(type(value), np.number):
            raise CheckError("I/V: current/voltage source value should be a complex number")
        if not np.issubdtype(type(element), np.number):
            raise CheckError("G/R: source internal conductance/resistance should be a float")


def check_data_problem(data_problem):
    """
    Check the solver problem data:
        - frequency
        - material definition
        - source definition
    """

    # check type
    if not isinstance(data_problem, dict):
        raise CheckError("data_problem: problem description should be a dict")

    # extract field
    freq = data_problem["freq"]
    material_def = data_problem["material_def"]
    source_def = data_problem["source_def"]

    # check type
    if not np.issubdtype(type(freq), np.floating):
        raise CheckError("freq: frequency should be a float")

    # check value
    if not(freq >= 0):
        raise CheckError("freq: frequency should be positive")

    # check material and source
    _check_material_def(material_def)
    _check_source_def(source_def)
