"""
Module for checking the plotter data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

from PyPEEC.lib_utils.error import CheckError


def _check_data_options(plot_type, data_options):
    """
    Check the validity of the data options.
    The data options are controlling the plot content.
    Three different types of plots are available:
        - material description (conductors, voltage sources, and current sources)
        - scalar plots (resistivity, potential, and current density)
        - arrow plots (current density)
    """

    # check type
    if not isinstance(data_options, dict):
        raise CheckError("data_options: data options should be a dict")

    # list of allowed variable names
    var_list = ["rho", "V_re", "V_im", "V_abs", "J_norm_abs", "J_norm_re", "J_norm_im"]
    vec_list = ["J_vec_re", "J_vec_im"]

    # check the options for scalar, arrow, and material plots
    if (plot_type == "scalar") or (plot_type == "arrow") or (plot_type == "material"):
        # check type
        if not isinstance(data_options["plot_title"], str):
            raise CheckError("plot_title: plot title option should be a string")
        if not isinstance(data_options["plot_legend"], str):
            raise CheckError("plot_legend: plot legend option should be a string")

    # check the options for scalar and arrow plots
    if (plot_type == "scalar") or (plot_type == "arrow"):
        # check type
        if not isinstance(data_options["var"], str):
            raise CheckError("var: the var option should be a string")
        if not isinstance(data_options["scale"], float):
            raise CheckError("scale: the scale option should be a float")
        if not isinstance(data_options["log"], bool):
            raise CheckError("log: the log option should be a boolean")

        # check size
        if not (len(data_options["color_lim"]) == 2):
            raise CheckError("color_lim: invalid color limits (should be a list with tep elements)")
        if not (len(data_options["filter_lim"]) == 2):
            raise CheckError("filter_lim: invalid filter limits (should be a list with tep elements)")

        # check value
        if not (data_options["var"] in var_list):
            raise CheckError("var: var option does not exist")
        if not (data_options["scale"] > 0):
            raise CheckError("scale: the scale option should be greater than zero")
        if not all(isinstance(x, float) or (x is None) for x in data_options["color_lim"]):
            raise CheckError("color_lim: color limits should be composed of floats")
        if not all(isinstance(x, float) or (x is None) for x in data_options["filter_lim"]):
            raise CheckError("filter_lim: filter limits should be composed of floats")

    # check the options for arrow plots
    if plot_type == "arrow":
        # check type
        if not isinstance(data_options["vec"], str):
            raise CheckError("vec: the vec option should be a string")
        if not isinstance(data_options["arrow_scale"], float):
            raise CheckError("arrow_scale: the arrow relative scaling should be a float")
        if not isinstance(data_options["arrow_threshold"], float):
            raise CheckError("arrow_threshold: the arrow removal threshold should be a float")

        # check value
        if not (data_options["vec"] in vec_list):
            raise CheckError("vec: vec option does not exist")
        if not (data_options["arrow_scale"] > 0):
            raise CheckError("arrow_scale: the arrow relative scaling should be greater than zero")
        if not (data_options["arrow_threshold"] > 0):
            raise CheckError("arrow_threshold: the arrow removal threshold should be greater than zero")


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


def _check_data_plotter_item(data_plotter):
    """
    Check the validity of the dict describing a single plot.
    """

    # check type
    if not isinstance(data_plotter, dict):
        raise CheckError("data_plotter: plot description should be a dict")

    # extract field
    plot_type = data_plotter["plot_type"]
    data_window = data_plotter["data_window"]
    data_options = data_plotter["data_options"]
    plot_options = data_plotter["plot_options"]

    # check type
    if not isinstance(plot_type, str):
        raise CheckError("plot_type: plot type should be a string")

    # check value
    if plot_type not in ["material", "scalar", "arrow"]:
        raise CheckError("plot_type: specified plot type does not exist")

    # check data
    _check_data_window(data_window)
    _check_data_options(plot_type, data_options)
    _check_plot_options(plot_options)


def check_data_plotter(data_plotter):
    """
    Check the type of the data defining several plots.
    """

    # check type
    if not isinstance(data_plotter, list):
        raise CheckError("data_plotter: plot data should be a list")

    # check items
    for dat_tmp in data_plotter:
        _check_data_plotter_item(dat_tmp)


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
