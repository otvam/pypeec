"""
Module for checking the viewer and plotter data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

from PyPEEC.lib_utils.error import CheckError


def _check_data_window(data_window):
    """
    Check the plot window options (for the viewer and plotter).
    Check the window title, window size, and menu configuration.
    """

    # get the data
    title = data_window["title"]
    show_menu = data_window["show_menu"]
    window_size = data_window["window_size"]

    # check type
    if not isinstance(title, str):
        raise CheckError("title: window title should be a string")
    if not isinstance(show_menu, bool):
        raise CheckError("show_menu: menu toggle switch should be a boolean")

    # check size
    if not len(window_size) == 2:
        raise CheckError("window_size: invalid window size (should be a list with two elements)")

    # check value
    if not all(isinstance(x, int) for x in window_size):
        raise CheckError("window_size: window_size: window size should be composed of integers")
    if not all((x >= 1) for x in window_size):
        raise CheckError("window_size: window_size: window size should be greater than zero")


def _check_plot_options(plot_options):
    """
    Check the validity of the plot options (for the viewer and plotter).
    The plot options are controlling the wireframe rendering.
    """

    # check type
    if not isinstance(plot_options, dict):
        raise CheckError("plot_options: plot options should be a dict")

    # check type
    if not isinstance(plot_options["title"], str):
        raise CheckError("title: plot title should be a string")

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

    # check cloud options (plot of the point cloud)
    if not isinstance(plot_options["cloud_plot"], bool):
        raise CheckError("cloud_plot: the cloud plot option should be a boolean")
    if not isinstance(plot_options["cloud_size"], float):
        raise CheckError("cloud_size: the cloud size option should be a float")
    if not isinstance(plot_options["cloud_color"], str):
        raise CheckError("cloud_color: the cloud color option should be a string")
    if not isinstance(plot_options["cloud_opacity"], float):
        raise CheckError("cloud_opacity: the cloud opacity option should be a float")


def _check_clip_options(clip_options):
    """
    Check the validity of the clip options (for the viewer and plotter).
    The clip options are controlling the cut plane (clipping) of the plots.
    """

    # check type
    if not isinstance(clip_options, dict):
        raise CheckError("clip_options: clip options should be a dict")

    # check type
    if not isinstance(clip_options["clip_plot"], bool):
        raise CheckError("clip_plot: the clip plot option should be a boolean")
    if not isinstance(clip_options["clip_invert"], bool):
        raise CheckError("clip_invert: the clip invert option should be a boolean")
    if not isinstance(clip_options["clip_axis"], str):
        raise CheckError("clip_axis: the axis of the clip should be a string")
    if not clip_options["clip_axis"] in ["x", "y", "z"]:
        raise CheckError("clip_axis: the axis of the clip is invalid")
    if not isinstance(clip_options["clip_value"], float):
        raise CheckError("clip_value: the value of the clip plane should be a float")


def _check_data_options_plotter_pyvista(plot_type, data_options):
    """
    Check the validity of the data options (for the plotter).
    The data options are controlling the plot content.
    Three different types of plots are available:
        - material description
        - scalar plots
        - arrow plots
    """

    # check type
    if not isinstance(data_options, dict):
        raise CheckError("data_options: data options should be a dict")

    # list of allowed variable names
    var_voxel_list = [
        "V_c_re", "V_c_im", "V_c_abs",
        "V_m_re", "V_m_im", "V_m_abs",
        "S_c_re", "S_c_im", "S_c_abs",
        "Q_m_re", "Q_m_im", "Q_m_abs",
        "J_c_norm_abs", "J_c_norm_re", "J_c_norm_im",
        "B_m_norm_abs", "B_m_norm_re", "B_m_norm_im",
        "P_c_abs", "P_m_abs",
    ]
    vec_voxel_list = [
        "J_c_vec_re", "J_c_vec_im",
        "B_m_vec_re", "B_m_vec_im",
    ]
    var_point_list = ["H_norm_abs", "H_norm_re", "H_norm_im"]
    vec_point_list = ["H_vec_re", "H_vec_im"]

    # check the material options
    if plot_type == "material":
        if not isinstance(data_options["color_electric"], str):
            raise CheckError("color_electric: color name should be a string")
        if not isinstance(data_options["color_magnetic"], str):
            raise CheckError("color_magnetic: color name should be a string")
        if not isinstance(data_options["color_current_source"], str):
            raise CheckError("color_current_source: color name should be a string")
        if not isinstance(data_options["color_voltage_source"], str):
            raise CheckError("color_voltage_source: color name should be a string")

    # check the scalar options
    if plot_type in ["scalar_voxel", "scalar_point"]:
        # check type
        if not isinstance(data_options["var"], str):
            raise CheckError("var: scalar variable name should be a string")
        if not isinstance(data_options["point_size"], float):
            raise CheckError("point_size: the marker size option should be a float")

        # check compatibility
        if plot_type == "scalar_voxel":
            if not (data_options["var"] in var_voxel_list):
                raise CheckError("var: scalar variable name is invalid for this plot type and geometry")
        elif plot_type == "scalar_point":
            if not (data_options["var"] in var_point_list):
                raise CheckError("var: scalar variable name is invalid for this plot type and geometry")
        else:
            raise CheckError("plot_geom: the plot geometry option is incompatible with the plot type")

    # check the arrow options
    if plot_type in ["arrow_voxel", "arrow_point"]:
        # check type
        if not isinstance(data_options["var_scalar"], str):
            raise CheckError("var_scalar: scalar variable name should be a string")
        if not isinstance(data_options["var_vector"], str):
            raise CheckError("var_vector: vector variable name should be a string")
        if not isinstance(data_options["arrow_scale"], float):
            raise CheckError("arrow_scale: the arrow relative scaling should be a float")
        if not isinstance(data_options["arrow_threshold"], float):
            raise CheckError("arrow_threshold: the arrow removal threshold should be a float")

        # check value
        if not (data_options["arrow_scale"] > 0):
            raise CheckError("arrow_scale: the arrow relative scaling should be greater than zero")
        if not (data_options["arrow_threshold"] > 0):
            raise CheckError("arrow_threshold: the arrow removal threshold should be greater than zero")

        # check compatibility
        if plot_type == "arrow_voxel":
            if not (data_options["var_scalar"] in var_voxel_list):
                raise CheckError("var_scalar: scalar variable name is invalid for this plot type and geometry")
            if not (data_options["var_vector"] in vec_voxel_list):
                raise CheckError("var_vector: vector variable name is invalid for this plot type and geometry")
        elif plot_type == "arrow_point":
            if not (data_options["var_scalar"] in var_point_list):
                raise CheckError("var_scalar: scalar variable name is invalid for this plot type and geometry")
            if not (data_options["var_vector"] in vec_point_list):
                raise CheckError("var_vector: vector variable name is invalid for this plot type and geometry")
        else:
            raise CheckError("plot_geom: the plot geometry option is incompatible with the plot type")

    # check the options for scalar and arrow plots
    if plot_type in ["scalar_voxel", "scalar_point", "arrow_voxel", "arrow_point"]:
        # check type
        if not isinstance(data_options["scale"], float):
            raise CheckError("scale: the scale option should be a float")
        if not isinstance(data_options["log"], bool):
            raise CheckError("log: the log option should be a boolean")
        if not isinstance(data_options["legend"], str):
            raise CheckError("plot_legend: plot legend option should be a string")

        # check size
        if not (len(data_options["color_lim"]) == 2):
            raise CheckError("color_lim: invalid color limits (should be a list with tep elements)")
        if not (len(data_options["filter_lim"]) == 2):
            raise CheckError("filter_lim: invalid filter limits (should be a list with tep elements)")

        # check value
        if not (data_options["scale"] > 0):
            raise CheckError("scale: the scale option should be greater than zero")
        if not all(isinstance(x, float) or (x is None) for x in data_options["color_lim"]):
            raise CheckError("color_lim: color limits should be composed of floats")
        if not all(isinstance(x, float) or (x is None) for x in data_options["filter_lim"]):
            raise CheckError("filter_lim: filter limits should be composed of floats")


def _check_data_options_plotter_matplotlib(plot_type, data_options):
    """
    Check the validity of the data options (for the plotter).
    The data options are controlling the plot content.
    Three different types of plots are available:
        - convergence
        - residuum
    """

    # check type
    if not isinstance(data_options, dict):
        raise CheckError("data_options: data options should be a dict")

    # check the convergence options
    if plot_type == "convergence":
        if not isinstance(data_options["color"], str):
            raise CheckError("color: color name should be a string")
        if not isinstance(data_options["marker"], str):
            raise CheckError("marker: marker name should be a string")

    # check the residuum options
    if plot_type == "residuum":
        if not isinstance(data_options["n_bins"], int):
            raise CheckError("n_bins: number of bins should be an integer")
        if not isinstance(data_options["edge_color"], str):
            raise CheckError("edge_color: color name should be a string")
        if not isinstance(data_options["bar_color"], str):
            raise CheckError("bar_color: color name should be a string")


def _check_data_options_viewer(plot_type, data_options):
    """
    Check the validity of the data options (for the viewer).
    The data options are controlling the plot content.
    Three different types of plots are available:
        - domain description
        - connection description
        - tolerance plot
    """

    # check type
    if not isinstance(data_options, dict):
        raise CheckError("data_options: data options should be a dict")

    # check the material options
    if plot_type == "voxelization":
        if not isinstance(data_options["color_voxel"], str):
            raise CheckError("color_voxel: color name should be a string")
        if not isinstance(data_options["color_reference"], str):
            raise CheckError("color_reference: color name should be a string")
        if not isinstance(data_options["opacity_voxel"], float):
            raise CheckError("opacity_voxel: the opacity option should be a float")
        if not isinstance(data_options["opacity_reference"], float):
            raise CheckError("opacity_reference: the opacity option should be a float")

    # check the scalar options
    if plot_type in ["domain", "connection"]:
        # check type
        if not isinstance(data_options["colormap"], str):
            raise CheckError("colormap: colormap name should be a string")
        if not isinstance(data_options["opacity"], float):
            raise CheckError("opacity: the opacity option should be a float")


def _check_data_plotter_matplotlib(data_plot):
    """
    Check the data describing a Matplotlib plot (for the plotter).
    """

    # check type
    if not isinstance(data_plot, dict):
        raise CheckError("data_plot: plot data should be a dict")

    # get the data
    plot_type = data_plot["plot_type"]
    data_options = data_plot["data_options"]

    # check type
    if not isinstance(plot_type, str):
        raise CheckError("plot_type: plot type should be a string")

    # check value
    if plot_type not in ["convergence", "residuum"]:
        raise CheckError("data_plot: specified data plot is invalid")
    
    # check data
    _check_data_options_plotter_matplotlib(plot_type, data_options)


def _check_data_plotter_pyvista(data_plot):
    """
    Check the data describing a PyVista plot (for the plotter).
    """

    # check type
    if not isinstance(data_plot, dict):
        raise CheckError("data_plot: plot data should be a dict")

    # get the data
    plot_type = data_plot["plot_type"]
    data_options = data_plot["data_options"]
    clip_options = data_plot["clip_options"]
    plot_options = data_plot["plot_options"]

    # check type
    if not isinstance(plot_type, str):
        raise CheckError("plot_type: plot type should be a string")

    # check value
    if plot_type not in ["material", "scalar_voxel", "scalar_point", "arrow_voxel", "arrow_point"]:
        raise CheckError("plot_type: specified plot type is invalid")

    # check data
    _check_data_options_plotter_pyvista(plot_type, data_options)
    _check_clip_options(clip_options)
    _check_plot_options(plot_options)


def _check_data_plotter_item(data_plotter):
    """
    Check the validity of the dict describing a single plot (for the plotter).
    """

    # check type
    if not isinstance(data_plotter, dict):
        raise CheckError("data_plotter: plot description should be a dict")

    # extract field
    plot_framework = data_plotter["plot_framework"]
    data_window = data_plotter["data_window"]
    data_plot = data_plotter["data_plot"]

    # check window data
    _check_data_window(data_window)

    # check framework
    if not isinstance(plot_framework, str):
        raise CheckError("plot_framework: plot framework should be a string")

    # check the plot data for the framework
    if plot_framework == "matplotlib":
        _check_data_plotter_matplotlib(data_plot)
    elif plot_framework == "pyvista":
        _check_data_plotter_pyvista(data_plot)
    else:
        raise CheckError("plot_framework: plot framework is invalid")


def _check_data_viewer_item(data_viewer):
    """
    Check the validity of the dict describing a single plot (for the viewer).
    """

    # check type
    if not isinstance(data_viewer, dict):
        raise CheckError("data_viewer: the plot description should be a dict")

    # extract field
    data_window = data_viewer["data_window"]
    data_plot = data_viewer["data_plot"]

    # check window data
    _check_data_window(data_window)

    # check plot data
    if not isinstance(data_plot, dict):
        raise CheckError("data_plot: plot data should be a dict")

    # get the data
    plot_type = data_plot["plot_type"]
    clip_options = data_plot["clip_options"]
    data_options = data_plot["data_options"]
    plot_options = data_plot["plot_options"]

    # check plot type
    if not isinstance(plot_type, str):
        raise CheckError("plot_type: plot type should be a string")
    if plot_type not in ["domain", "connection", "voxelization"]:
        raise CheckError("plot_type: specified plot type is invalid")

    # check options
    _check_data_options_viewer(plot_type, data_options)
    _check_clip_options(clip_options)
    _check_plot_options(plot_options)


def check_data_plotter(data_plotter):
    """
    Check the type of the data defining several plots.
    This function is used for the plotter.
    """

    # check type
    if not isinstance(data_plotter, list):
        raise CheckError("data_plotter: plot data should be a list")

    # check items
    for data_plotter_tmp in data_plotter:
        _check_data_plotter_item(data_plotter_tmp)


def check_data_viewer(data_viewer):
    """
    Check the type of the data defining several plots.
    This function is used for the viewer.
    """

    # check type
    if not isinstance(data_viewer, list):
        raise CheckError("data_viewer: plot data should be a list")

    # check items
    for data_viewer_tmp in data_viewer:
        _check_data_viewer_item(data_viewer_tmp)
