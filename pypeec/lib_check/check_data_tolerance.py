"""
Module for checking the solver tolerance data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

from pypeec.lib_utils import datachecker


def _check_solver_options(solver_options):
    """
    Check the matrix solver options.
    """

    # check type
    key_list = ["tolerance", "gmres_options"]
    datachecker.check_dict("solver_options", solver_options, key_list=key_list)

    # extract field
    tolerance = solver_options["tolerance"]
    gmres_options = solver_options["gmres_options"]

    # check type
    key_list = ["rel_tol", "abs_tol", "n_between_restart", "n_maximum_restart"]
    datachecker.check_dict("gmres_options", gmres_options, key_list=key_list)

    # check the data
    datachecker.check_float("tolerance", tolerance, is_positive=True, can_be_zero=False)
    datachecker.check_float("rel_tol", gmres_options["rel_tol"], is_positive=True, can_be_zero=False)
    datachecker.check_float("abs_tol", gmres_options["abs_tol"], is_positive=True, can_be_zero=False)
    datachecker.check_integer("n_between_restart", gmres_options["n_between_restart"], is_positive=True, can_be_zero=False)
    datachecker.check_integer("n_maximum_restart", gmres_options["n_maximum_restart"], is_positive=True, can_be_zero=False)


def _check_condition_options(condition_options):
    """
    Check the matrix condition number checking options.
    """

    # check type
    key_list = ["check", "tolerance", "norm_options"]
    datachecker.check_dict("condition_options", condition_options, key_list=key_list)

    # extract field
    check = condition_options["check"]
    tolerance = condition_options["tolerance"]
    norm_options = condition_options["norm_options"]

    # check type
    key_list = ["t_accuracy", "n_iter_max"]
    datachecker.check_dict("norm_options", norm_options, key_list=key_list)

    # check the data
    datachecker.check_boolean("tolerance", check)
    datachecker.check_float("tolerance", tolerance, is_positive=True, can_be_zero=False)
    datachecker.check_integer("t_accuracy", norm_options["t_accuracy"], is_positive=True, can_be_zero=False)
    datachecker.check_integer("n_iter_max", norm_options["n_iter_max"], is_positive=True, can_be_zero=False)


def check_data_tolerance(data_tolerance):
    """
    Check the solver tolerance data:
        - Green functions
        - solver options
        - matrix condition options
    """

    # check type
    key_list = ["green_simplify", "coupling_simplify", "solver_options", "condition_options"]
    datachecker.check_dict("data_tolerance", data_tolerance, key_list=key_list)

    # extract field
    green_simplify = data_tolerance["green_simplify"]
    coupling_simplify = data_tolerance["coupling_simplify"]
    solver_options = data_tolerance["solver_options"]
    condition_options = data_tolerance["condition_options"]

    # check data
    datachecker.check_float("green_simplify", green_simplify, is_positive=True, can_be_zero=False)
    datachecker.check_float("coupling_simplify", coupling_simplify, is_positive=True, can_be_zero=False)

    # check solver and condition check options
    _check_solver_options(solver_options)
    _check_condition_options(condition_options)
