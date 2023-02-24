"""
Module for checking the solver tolerance data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

from PyPEEC.lib_check import check_data_base


def _check_solver_options(solver_options):
    """
    Check the matrix solver options.
    """

    # check type
    key_list = [
        "tolerance",
        "gmres_options",
    ]
    check_data_base.check_dict("solver_options", solver_options, str_key=True, key_list=key_list)

    # extract field
    tolerance = solver_options["tolerance"]
    gmres_options = solver_options["gmres_options"]

    # check type
    key_list = [
        "rel_tol",
        "abs_tol",
        "n_between_restart",
        "n_maximum_restart",
    ]
    check_data_base.check_dict("gmres_options", gmres_options, str_key=True, key_list=key_list)

    # check the data
    check_data_base.check_float("tolerance", tolerance, is_positive=True, can_be_zero=False)
    check_data_base.check_float("rel_tol", gmres_options["rel_tol"], is_positive=True, can_be_zero=False)
    check_data_base.check_float("abs_tol", gmres_options["abs_tol"], is_positive=True, can_be_zero=False)
    check_data_base.check_integer("n_between_restart", gmres_options["n_between_restart"], is_positive=True, can_be_zero=False)
    check_data_base.check_integer("n_maximum_restart", gmres_options["n_maximum_restart"], is_positive=True, can_be_zero=False)


def _check_condition_options(condition_options):
    """
    Check the matrix condition number checking options.
    """

    # check type
    key_list = [
        "check",
        "tolerance",
        "norm_options",
    ]
    check_data_base.check_dict("condition_options", condition_options, str_key=True, key_list=key_list)

    # extract field
    check = condition_options["check"]
    tolerance = condition_options["tolerance"]
    norm_options = condition_options["norm_options"]

    # check type
    key_list = [
        "t_accuracy",
        "n_iter_max",
    ]
    check_data_base.check_dict("norm_options", norm_options, str_key=True, key_list=key_list)

    # check the data
    check_data_base.check_boolean("tolerance", check)
    check_data_base.check_float("tolerance", tolerance, is_positive=True, can_be_zero=False)
    check_data_base.check_integer("t_accuracy", norm_options["t_accuracy"], is_positive=True, can_be_zero=False)
    check_data_base.check_integer("n_iter_max", norm_options["n_iter_max"], is_positive=True, can_be_zero=False)


def check_data_tolerance(data_tolerance):
    """
    Check the solver tolerance data:
        - Green functions
        - solver options
        - matrix condition options
    """

    # check type
    key_list = [
        "green_simplify",
        "coupling_simplify",
        "solver_options",
        "condition_options",
    ]
    check_data_base.check_dict("data_tolerance", data_tolerance, str_key=True, key_list=key_list)

    # extract field
    green_simplify = data_tolerance["green_simplify"]
    coupling_simplify = data_tolerance["coupling_simplify"]
    solver_options = data_tolerance["solver_options"]
    condition_options = data_tolerance["condition_options"]

    # check data
    check_data_base.check_float("green_simplify", green_simplify, is_positive=True, can_be_zero=False)
    check_data_base.check_float("coupling_simplify", coupling_simplify, is_positive=True, can_be_zero=False)

    # check solver and condition check options
    _check_solver_options(solver_options)
    _check_condition_options(condition_options)
