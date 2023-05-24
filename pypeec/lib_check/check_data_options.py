"""
Module for the user provided options.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

from pypeec.lib_check import datachecker


def check_tag_list(data_check, tag_list):
    """
    Check the list of plots to be shown.
    """

    # check the list of plots
    if tag_list is not None:
        datachecker.check_list("tag", tag_list, can_be_empty=True, sub_type=str)
        for tag in tag_list:
            datachecker.check_choice("tag", tag, data_check)


def check_plot_options(is_silent, folder):
    """
    Check the plot mode (display or not the plots).
    """

    datachecker.check_boolean("is_silent", is_silent)
    if folder is not None:
        datachecker.check_folder("folder", folder)


def check_data_options(is_truncated):
    """
    Check the plot mode (display or not the plots).
    """

    datachecker.check_boolean("is_truncated", is_truncated)
