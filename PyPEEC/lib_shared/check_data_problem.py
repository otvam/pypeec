"""
Module for checking the solver problem data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np
from PyPEEC.lib_utils.error import CheckError


def _check_conductor_def(conductor_def):
    """
    Check that the conductor definition is valid.
    """

    # check type
    if not isinstance(conductor_def, dict):
        raise CheckError("conductor_def: conductor definition should be a dict")

    # check value
    for tag, dat_tmp in conductor_def.items():
        # extract the data
        domain = dat_tmp["domain"]
        rho = dat_tmp["rho"]

        # check type
        if not isinstance(tag, str):
            raise CheckError("tag: conductor name should be a string")
        if not np.issubdtype(type(rho), np.floating):
            raise CheckError("rho: conductor resistivity should be a float")

        # check value
        if not np.isscalar(rho):
            raise CheckError("rho: conductor resistivity should be a real scalar")
        if not (rho > 0):
            raise CheckError("rho: conductor resistivity should be greater than zero")
        if not all(np.issubdtype(type(x), str) for x in domain):
            raise CheckError("domain: domain name should be composed of strings")


def _check_source_def(source_def):
    """
    Check that the source definition is valid.
    """

    # check type
    if not isinstance(source_def, dict):
        raise CheckError("source_def: source definition should be a dict")

    # check value
    for tag, dat_tmp in source_def.items():
        # extract the data
        source_type = dat_tmp["source_type"]
        domain = dat_tmp["domain"]

        # check type
        if not isinstance(tag, str):
            raise CheckError("tag: source name should be a string")
        if not isinstance(source_type, str):
            raise CheckError("source_type: source type should be a string")

        # check value
        if not (source_type in ["current", "voltage"]):
            raise CheckError("source_type: source type should be voltage or current")
        if not all(np.issubdtype(type(x), str) for x in domain):
            raise CheckError("domain: domain name should be composed of strings")

        # get the source value
        if source_type == "current":
            value = dat_tmp["I"]
            element = dat_tmp["G"]
        elif source_type == "voltage":
            value = dat_tmp["V"]
            element = dat_tmp["R"]
        else:
            raise CheckError("invalid source type")

        # check the source type
        if not np.issubdtype(type(value), np.number):
            raise CheckError("I/V: current/voltage source value should be a complex number")
        if not np.issubdtype(type(element), np.floating):
            raise CheckError("G/R: source internal conductance/resistance should be a float")

        # check the source value
        if not np.isscalar(value):
            raise CheckError("I/V: current/voltage source value should be a scalar")
        if not np.isscalar(element):
            raise CheckError("G/R: source internal conductance/resistance should be a real scalar")


def check_data_problem(data_problem):
    """
    Check the solver problem data:
        - Green function
        - frequency
        - solver options
        - matrix condition options
        - conductor definition
        - source definition
    """

    # check type
    if not isinstance(data_problem, dict):
        raise CheckError("data_problem: problem description should be a dict")

    # extract field
    n_green = data_problem["n_green"]
    freq = data_problem["freq"]
    solver_options = data_problem["solver_options"]
    condition_options = data_problem["condition_options"]
    conductor_def = data_problem["conductor_def"]
    source_def = data_problem["source_def"]

    # check type
    if not np.issubdtype(type(freq), np.floating):
        raise CheckError("freq: frequency should be a float")
    if not np.issubdtype(type(n_green), np.floating):
        raise CheckError("n_green: voxel distance to simplify the green function should be a float")

    # check value
    if not(freq >= 0):
        raise CheckError("freq: frequency should be positive")
    if not (n_green > 0):
        raise CheckError("n_green: voxel distance to simplify the green function should be positive")

    # check solver options
    if not isinstance(solver_options, dict):
        raise CheckError("solver_options: solver options should be a dict")
    if not (solver_options["tol"] > 0):
        raise CheckError("tol: solver relative tolerance should be greater than zero")
    if not (solver_options["atol"] > 0):
        raise CheckError("solver absolute tolerance should be greater than zero")
    if not (solver_options["restart"] >= 1):
        raise CheckError("number of iterations between restarts should be greater than zero")
    if not (solver_options["maxiter"] >= 1):
        raise CheckError("number of restart cycles should be greater than zero")

    # check condition options
    if not isinstance(condition_options, dict):
        raise CheckError("solver options should be a dict")
    if not isinstance(condition_options["check"], bool):
        raise CheckError("the flag for checking the condition should be a boolean")
    if not (condition_options["tolerance"] > 0):
        raise CheckError("maximum condition number tolerance should be greater than zero")
    if not (condition_options["accuracy"] > 0):
        raise CheckError("condition number accuracy should be greater than zero")

    # check conductor and source
    _check_conductor_def(conductor_def)
    _check_source_def(source_def)
