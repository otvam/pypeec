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


def check_plot_options(plot_mode, folder):
    """
    Check the plot mode (display or not the plots).
    """

    datachecker.check_choice("plot_mode", plot_mode, ["qt", "nb", "save", "none"])
    datachecker.check_folder("folder", folder, can_be_none=True)


def check_data_options(is_truncated):
    """
    Check the plot mode (display or not the plots).
    """

    datachecker.check_boolean("is_truncated", is_truncated)
