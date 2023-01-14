"""
Module for checking the viewer data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

from PyPEEC.lib_utils.error import CheckError


def _check_plot_options(plot_options):
    """
    Check the validity of the plot options.
    The plot options are controlling the wireframes and the origin marker.
    """

    # check type
    if not isinstance(plot_options, dict):
        raise CheckError("plot_options: plot options should be a dict")

    # check grid options (plot of the complete grid as wireframes)
    if not isinstance(plot_options["grid_plot"], bool):
        raise CheckError("grid_plot: the grid plot option should be a boolean")
    if not isinstance(plot_options["grid_thickness"], float):
        raise CheckError("grid_thickness: the grid thickness option should be a float")
    if not isinstance(plot_options["grid_color"], str):
        raise CheckError("grid_color: the grid color option should be a string")
    if not isinstance(plot_options["grid_opacity"], float):
        raise CheckError("grid_opacity: the grid opacity option should be a float")

    # check geom options (plot of the non-empty voxels as wireframe)
    if not isinstance(plot_options["geom_plot"], bool):
        raise CheckError("geom_plot: the geom plot option should be a boolean")
    if not isinstance(plot_options["geom_thickness"], float):
        raise CheckError("geom_thickness: the geom thickness option should be a float")
    if not isinstance(plot_options["geom_color"], str):
        raise CheckError("geom_color: the geom color option should be a string")
    if not isinstance(plot_options["geom_opacity"], float):
        raise CheckError("geom_opacity: the geom opacity option should be a float")

    # check origin options (add a marker at the origin)
    if not isinstance(plot_options["origin_plot"], bool):
        raise CheckError("origin_plot: the origin plot option should be a boolean")
    if not isinstance(plot_options["origin_size"], float):
        raise CheckError("origin_size: the origin size option should be a float")
    if not isinstance(plot_options["origin_color"], str):
        raise CheckError("origin_color: the origin color option should be a string")


def _check_data_window(data_window):
    """
    Check the plot window options (window title, window size, and type).
    """

    # get the data
    title = data_window["title"]
    show_menu = data_window["show_menu"]
    size = data_window["size"]

    # check type
    if not isinstance(title, str):
        raise CheckError("title: window title should be a string")
    if not isinstance(show_menu, bool):
        raise CheckError("show_menu: menu toggle switch should be a boolean")

    # check size
    if not len(size) == 2:
        raise CheckError("size: invalid window size (should be a list with two elements)")

    # check value
    if not all(isinstance(x, int) for x in size):
        raise CheckError("size: window_size: window size should be composed of integers")
    if not all((x >= 1) for x in size):
        raise CheckError("size: window_size: window size should be greater than zero")


def check_data_viewer(data_viewer):
    """
    Check the validity of the dict describing a 3D voxel structure plot.
    """

    # check type
    if not isinstance(data_viewer, dict):
        raise CheckError("data_viewer: the plot description should be a dict")

    # extract field
    plot_title = data_viewer["plot_title"]
    data_window = data_viewer["data_window"]
    plot_options = data_viewer["plot_options"]

    # check type
    if not isinstance(plot_title, str):
        raise CheckError("plot_title: plot title should be a string")

    # check data
    _check_data_window(data_window)
    _check_plot_options(plot_options)
