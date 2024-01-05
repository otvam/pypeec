"""
Module for the user provided options.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

from pypeec.lib_check import datachecker


def check_tag_list(data_check, tag_list):
    """
    Check the list of plots to be shown.
    """

    # check the list of plots
    datachecker.check_list("tag_list", tag_list, can_be_empty=True, sub_type=str, can_be_none=True)
    if tag_list is not None:
        for tag in tag_list:
            datachecker.check_choice("tag_list", tag, data_check)


def check_plot_options(plot_mode, folder, name):
    """
    Check the plot mode (display or not the plots).
    """

    datachecker.check_choice("plot_mode", plot_mode, ["qt", "nb", "save", "none"])
    datachecker.check_string("name", name, can_be_empty=False, can_be_none=True)
    datachecker.check_folder("folder", folder, can_be_none=True)


def check_data_options(is_truncated):
    """
    Check the plot mode (display or not the plots).
    """

    datachecker.check_boolean("is_truncated", is_truncated)


def check_data_voxel(data_voxel):
    """
    Check the voxel data.
    """

    # extract field
    key_list = ["duration", "is_truncated", "data_geom"]
    datachecker.check_dict("data_voxel", data_voxel, key_list=key_list)

    is_truncated = data_voxel["is_truncated"]
    data_geom = data_voxel["data_geom"]

    # check data
    datachecker.check_dict("data_geom", data_geom)
    datachecker.check_boolean("is_truncated", is_truncated)
    datachecker.check_assert("is_truncated", not is_truncated, "truncated input data cannot be used")

    return data_geom


def check_data_solution(data_solution):
    """
    Check the solution data.
    """

    # extract field
    key_list = ["duration", "is_truncated", "data_init", "data_sweep"]
    datachecker.check_dict("data_solution", data_solution, key_list=key_list)

    is_truncated = data_solution["is_truncated"]
    data_init = data_solution["data_init"]
    data_sweep = data_solution["data_sweep"]

    # check data
    datachecker.check_dict("data_geom", data_init)
    datachecker.check_dict("data_geom", data_sweep)
    datachecker.check_boolean("is_truncated", is_truncated)
    datachecker.check_assert("is_truncated", not is_truncated, "truncated input data cannot be used")

    return data_init, data_sweep
