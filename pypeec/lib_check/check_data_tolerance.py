"""
Module for checking the solver tolerance data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

from pypeec.lib_check import datachecker


def _check_solver_options(solver_options):
    """
    Check the matrix solver options.
    """

    # check type
    key_list = ["check", "tolerance", "iter_options"]
    datachecker.check_dict("solver_options", solver_options, key_list=key_list)

    # extract field
    check = solver_options["check"]
    tolerance = solver_options["tolerance"]
    iter_options = solver_options["iter_options"]

    # check type
    key_list = ["solver", "rel_tol", "abs_tol", "n_inner", "n_outer"]
    datachecker.check_dict("iter_options", iter_options, key_list=key_list)

    # check the data
    datachecker.check_boolean("tolerance", check)
    datachecker.check_float("tolerance", tolerance, is_positive=True, can_be_zero=False)
    datachecker.check_choice("solver", iter_options["solver"], ["GMRES", "GCROT"])
    datachecker.check_float("rel_tol", iter_options["rel_tol"], is_positive=True, can_be_zero=False)
    datachecker.check_float("abs_tol", iter_options["abs_tol"], is_positive=True, can_be_zero=False)
    datachecker.check_integer("n_inner", iter_options["n_inner"], is_positive=True, can_be_zero=False)
    datachecker.check_integer("n_outer", iter_options["n_outer"], is_positive=True, can_be_zero=False)


def _check_condition_options(condition_options):
    """
    Check the matrix condition number check options.
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
