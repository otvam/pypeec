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
    if not conductor_def:
        raise CheckError("conductor_def: conductor definition cannot be empty")

    # check value
    for tag, dat_tmp in conductor_def.items():
        # extract the data
        domain_list = dat_tmp["domain_list"]
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
        if not all(np.issubdtype(type(x), str) for x in domain_list):
            raise CheckError("domain_list: domain name should be composed of strings")


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

        # check value
        if not (source_type in ["current", "voltage"]):
            raise CheckError("source_type: source type should be voltage or current")
        if not all(np.issubdtype(type(x), str) for x in domain_list):
            raise CheckError("domain_list: domain name should be composed of strings")

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


def _check_solver_options(solver_options):
    """
    Check the matrix solver options.
    """

    # check the type
    if not isinstance(solver_options, dict):
        raise CheckError("solver_options: solver options should be a dict")

    # check the data
    if not (solver_options["rel_tol"] > 0):
        raise CheckError("rel_tol: solver relative tolerance should be greater than zero")
    if not (solver_options["abs_tol"] > 0):
        raise CheckError("abs_tol: solver absolute tolerance should be greater than zero")
    if not (solver_options["n_between_restart"] >= 1):
        raise CheckError("n_between_restart: number of iterations between restarts should be greater than zero")
    if not (solver_options["n_maximum_restart"] >= 1):
        raise CheckError("n_maximum_restart: number of restart cycles should be greater than zero")

def _check_condition_options(condition_options):
    """
    Check the matrix condition number checking options.
    """

    # check the type
    if not isinstance(condition_options, dict):
        raise CheckError("solver options should be a dict")

    # extract field
    check = condition_options["check"]
    tolerance = condition_options["tolerance"]
    norm_options = condition_options["norm_options"]

    if not isinstance(check, bool):
        raise CheckError("check: the flag for checking the condition should be a boolean")
    if not (tolerance > 0):
        raise CheckError("tolerance: maximum condition number tolerance should be greater than zero")
    if not (norm_options["t_accuracy"] > 0):
        raise CheckError("t_accuracy: accuracy parameter for the norm be greater than zero")
    if not (norm_options["n_iter_max"] > 0):
        raise CheckError("n_iter_max: maximum number of iterations for the norm should be greater than zero")

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
    freq = data_problem["freq"]
    green_simplify = data_problem["green_simplify"]
    solver_options = data_problem["solver_options"]
    condition_options = data_problem["condition_options"]
    conductor_def = data_problem["conductor_def"]
    source_def = data_problem["source_def"]

    # check type
    if not np.issubdtype(type(freq), np.floating):
        raise CheckError("freq: frequency should be a float")
    if not np.issubdtype(type(green_simplify), np.floating):
        raise CheckError("green_simplify: voxel distance to simplify the green function should be a float")

    # check value
    if not(freq >= 0):
        raise CheckError("freq: frequency should be positive")
    if not (green_simplify > 0):
        raise CheckError("green_simplify: voxel distance to simplify the green function should be positive")


    # check solver and condition check options
    _check_solver_options(solver_options)
    _check_condition_options(condition_options)

    # check conductor and source
    _check_conductor_def(conductor_def)
    _check_source_def(source_def)
