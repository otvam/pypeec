"""
Module for checking the solver tolerance data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np
from PyPEEC.lib_utils.error import CheckError


def _check_solver_options(solver_options):
    """
    Check the matrix solver options.
    """

    # check the type
    if not isinstance(solver_options, dict):
        raise CheckError("solver_options: solver options should be a dict")

    # extract field
    gmres_options = solver_options["gmres_options"]

    # check the data
    if not (gmres_options["rel_tol"] > 0):
        raise CheckError("rel_tol: solver relative tolerance should be greater than zero")
    if not (gmres_options["abs_tol"] > 0):
        raise CheckError("abs_tol: solver absolute tolerance should be greater than zero")
    if not (gmres_options["n_between_restart"] >= 1):
        raise CheckError("n_between_restart: number of iterations between restarts should be greater than zero")
    if not (gmres_options["n_maximum_restart"] >= 1):
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


def check_data_tolerance(data_tolerance):
    """
    Check the solver tolerance data:
        - Green functions
        - solver options
        - matrix condition options
    """

    # check type
    if not isinstance(data_tolerance, dict):
        raise CheckError("data_tolerance: tolerance description should be a dict")

    # extract field
    green_simplify = data_tolerance["green_simplify"]
    coupling_simplify = data_tolerance["coupling_simplify"]
    solver_options = data_tolerance["solver_options"]
    condition_options = data_tolerance["condition_options"]

    # check type
    if not np.issubdtype(type(green_simplify), np.floating):
        raise CheckError("green_simplify: voxel distance to simplify the green functions should be a float")
    if not np.issubdtype(type(coupling_simplify), np.floating):
        raise CheckError("coupling_simplify: voxel distance to simplify the coupling functions should be a float")

    # check value
    if not (green_simplify > 0):
        raise CheckError("green_simplify: voxel distance to simplify the green functions should be positive")
    if not (coupling_simplify > 0):
        raise CheckError("coupling_simplify: voxel distance to simplify the coupling functions should be positive")

    # check solver and condition check options
    _check_solver_options(solver_options)
    _check_condition_options(condition_options)
