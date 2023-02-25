"""
Module for checking the viewer and plotter data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

from PyPEEC.lib_check import check_data_base


def _check_data_window(data_window):
    """
    Check the plot window options (for the viewer and plotter).
    Check the window title, window size, and menu configuration.
    """

    # check type
    key_list = ["title", "show_menu", "window_size"]
    check_data_base.check_dict("data_window", data_window, key_list=key_list)

    # get the data
    title = data_window["title"]
    show_menu = data_window["show_menu"]
    window_size = data_window["window_size"]

    # check data
    check_data_base.check_string("title", title)
    check_data_base.check_boolean("show_menu", show_menu)
    check_data_base.check_integer_array("window_size", window_size, size=2, is_positive=True, can_be_zero=False)


def _check_plot_options(plot_options):
    """
    Check the validity of the plot options (for the viewer and plotter).
    The plot options are controlling the wireframe rendering.
    """

    # check type
    key_list = [
        "title",
        "grid_plot", "grid_thickness", "grid_color", "grid_opacity",
        "geom_plot", "geom_thickness", "geom_color", "geom_opacity",
        "point_plot", "point_size", "point_color", "point_opacity",
    ]
    check_data_base.check_dict("data_window", plot_options, key_list=key_list)

    # check title data
    check_data_base.check_string("title", plot_options["title"])

    # check grid data
    check_data_base.check_boolean("grid_plot", plot_options["grid_plot"])
    check_data_base.check_float("grid_thickness", plot_options["grid_thickness"])
    check_data_base.check_string("grid_color", plot_options["grid_color"])
    check_data_base.check_float("grid_opacity", plot_options["grid_opacity"])

    # check geom data
    check_data_base.check_boolean("geom_plot", plot_options["geom_plot"])
    check_data_base.check_float("geom_thickness", plot_options["geom_thickness"])
    check_data_base.check_string("geom_color", plot_options["geom_color"])
    check_data_base.check_float("geom_opacity", plot_options["geom_opacity"])

    # check cloud data
    check_data_base.check_boolean("point_plot", plot_options["point_plot"])
    check_data_base.check_float("point_size", plot_options["point_size"])
    check_data_base.check_string("point_color", plot_options["point_color"])
    check_data_base.check_float("point_opacity", plot_options["point_opacity"])


def _check_clip_options(clip_options):
    """
    Check the validity of the clip options (for the viewer and plotter).
    The clip options are controlling the cut plane (clipping) of the plots.
    """

    # check type
    key_list = ["clip_plot", "clip_invert", "clip_axis", "clip_value"]
    check_data_base.check_dict("clip_options", clip_options, key_list=key_list)

    # check data
    check_data_base.check_boolean("clip_plot", clip_options["clip_plot"])
    check_data_base.check_boolean("clip_invert", clip_options["clip_invert"])
    check_data_base.check_choice("clip_axis", clip_options["clip_axis"], ["x", "y", "z"])
    check_data_base.check_float("clip_value", clip_options["clip_value"])


def _check_data_options_plotter_pyvista(plot_type, data_options):
    """
    Check the validity of the data options (for the plotter).
    The data options are controlling the plot content.
    Three different types of plots are available:
        - material description
        - scalar plots
        - arrow plots
    """

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
        # check type
        key_list = ["color_electric", "color_magnetic", "color_current_source", "color_voltage_source"]
        check_data_base.check_dict("data_options", data_options, key_list=key_list)

        # check data
        check_data_base.check_string("color_electric", data_options["color_electric"])
        check_data_base.check_string("color_magnetic", data_options["color_magnetic"])
        check_data_base.check_string("color_current_source", data_options["color_current_source"])
        check_data_base.check_string("color_voltage_source", data_options["color_voltage_source"])

    # check the options for scalar and arrow plots
    if plot_type in ["scalar_voxel", "scalar_point", "arrow_voxel", "arrow_point"]:
        # check type
        key_list = ["scale", "log", "legend", "color_lim", "filter_lim"]
        check_data_base.check_dict("data_options", data_options, key_list=key_list)

        # check data
        check_data_base.check_float("scale", data_options["scale"])
        check_data_base.check_boolean("log", data_options["log"])
        check_data_base.check_string("legend", data_options["legend"])
        if data_options["color_lim"] is not None:
            check_data_base.check_float_array("color_lim", data_options["color_lim"], size=2)
        if data_options["filter_lim"] is not None:
            check_data_base.check_float_array("filter_lim", data_options["filter_lim"], size=2)

    # check the scalar options
    if plot_type in ["scalar_voxel", "scalar_point"]:
        # check type
        key_list = ["var", "point_size"]
        check_data_base.check_dict("data_options", data_options, key_list=key_list)

        # check data
        check_data_base.check_string("var", data_options["var"])
        check_data_base.check_float("point_size", data_options["point_size"])

        # check compatibility
        if plot_type == "scalar_voxel":
            check_data_base.check_choice("var", data_options["var"], var_voxel_list)
        elif plot_type == "scalar_point":
            check_data_base.check_choice("var", data_options["var"], var_point_list)
        else:
            raise ValueError("plot_geom: the plot geometry option is incompatible with the plot type")

    # check the arrow options
    if plot_type in ["arrow_voxel", "arrow_point"]:
        # check type
        key_list = ["var_scalar", "var_vector", "arrow_scale", "arrow_threshold"]
        check_data_base.check_dict("data_options", data_options, key_list=key_list)

        # check data
        check_data_base.check_string("var_scalar", data_options["var_scalar"])
        check_data_base.check_string("var_vector", data_options["var_vector"])
        check_data_base.check_float("arrow_scale", data_options["arrow_scale"])
        check_data_base.check_float("arrow_threshold", data_options["arrow_threshold"])

        # check compatibility
        if plot_type == "arrow_voxel":
            check_data_base.check_choice("var_scalar", data_options["var_scalar"], var_voxel_list)
            check_data_base.check_choice("var_vector", data_options["var_vector"], vec_voxel_list)
        elif plot_type == "arrow_point":
            check_data_base.check_choice("var_scalar", data_options["var_scalar"], var_point_list)
            check_data_base.check_choice("var_vector", data_options["var_vector"], vec_point_list)
        else:
            raise ValueError("plot_geom: the plot geometry option is incompatible with the plot type")


def _check_data_options_plotter_matplotlib(plot_type, data_options):
    """
    Check the validity of the data options (for the plotter).
    The data options are controlling the plot content.
    Three different types of plots are available:
        - convergence
        - residuum
    """

    # check the convergence options
    if plot_type == "convergence":
        # check type
        key_list = ["color", "marker"]
        check_data_base.check_dict("data_options", data_options, key_list=key_list)

        # check data
        check_data_base.check_string("color", data_options["color"])
        check_data_base.check_string("marker", data_options["marker"])

    # check the residuum options
    if plot_type == "residuum":
        # check type
        key_list = ["n_bins", "edge_color", "bar_color"]
        check_data_base.check_dict("data_options", data_options, key_list=key_list)

        # check data
        check_data_base.check_integer("n_bins", data_options["n_bins"])
        check_data_base.check_string("edge_color", data_options["edge_color"])
        check_data_base.check_string("bar_color", data_options["bar_color"])


def _check_data_options_viewer(plot_type, data_options):
    """
    Check the validity of the data options (for the viewer).
    The data options are controlling the plot content.
    Three different types of plots are available:
        - domain description
        - connection description
        - tolerance plot
    """

    # check the material options
    if plot_type == "voxelization":
        # check type
        key_list = ["color_voxel", "color_reference", "opacity_voxel", "opacity_reference"]
        check_data_base.check_dict("data_options", data_options, key_list=key_list)

        # check data
        check_data_base.check_string("color_voxel", data_options["color_voxel"])
        check_data_base.check_string("color_reference", data_options["color_reference"])
        check_data_base.check_float("opacity_voxel", data_options["opacity_voxel"])
        check_data_base.check_float("opacity_reference", data_options["opacity_reference"])

    # check the scalar options
    if plot_type in ["domain", "connection"]:
        # check type
        key_list = ["colormap", "opacity"]
        check_data_base.check_dict("data_options", data_options, key_list=key_list)

        # check data
        check_data_base.check_string("colormap", data_options["colormap"])
        check_data_base.check_float("opacity", data_options["opacity"])


def _check_data_plotter_matplotlib(data_plot):
    """
    Check the data describing a Matplotlib plot (for the plotter).
    """

    # check type
    key_list = ["plot_type", "data_options"]
    check_data_base.check_dict("data_plot", data_plot, key_list=key_list)

    # get the data
    plot_type = data_plot["plot_type"]
    data_options = data_plot["data_options"]

    # check plot type
    check_data_base.check_choice("plot_type", plot_type, ["convergence", "residuum"])

    # check data
    _check_data_options_plotter_matplotlib(plot_type, data_options)


def _check_data_plotter_pyvista(data_plot):
    """
    Check the data describing a PyVista plot (for the plotter).
    """

    # check type
    key_list = ["plot_type", "clip_options", "data_options", "plot_options"]
    check_data_base.check_dict("data_plot", data_plot, key_list=key_list)

    # get the data
    plot_type = data_plot["plot_type"]
    data_options = data_plot["data_options"]
    clip_options = data_plot["clip_options"]
    plot_options = data_plot["plot_options"]

    # check plot type
    check_data_base.check_choice("plot_type", plot_type, ["material", "scalar_voxel", "scalar_point", "arrow_voxel", "arrow_point"])

    # check data
    _check_data_options_plotter_pyvista(plot_type, data_options)
    _check_clip_options(clip_options)
    _check_plot_options(plot_options)


def _check_data_plotter_item(data_plotter):
    """
    Check the validity of the dict describing a single plot (for the plotter).
    """

    # check type
    key_list = ["plot_framework", "data_window", "data_plot"]
    check_data_base.check_dict("data_plotter", data_plotter, key_list=key_list)

    # extract field
    plot_framework = data_plotter["plot_framework"]
    data_window = data_plotter["data_window"]
    data_plot = data_plotter["data_plot"]

    # check plot framework
    check_data_base.check_choice("plot_framework", plot_framework, ["matplotlib", "pyvista"])

    # check window data
    _check_data_window(data_window)

    # check the plot data for the framework
    if plot_framework == "matplotlib":
        _check_data_plotter_matplotlib(data_plot)
    elif plot_framework == "pyvista":
        _check_data_plotter_pyvista(data_plot)
    else:
        raise ValueError("plot_framework: plot framework is invalid")


def _check_data_viewer_item(data_viewer):
    """
    Check the validity of the dict describing a single plot (for the viewer).
    """

    # check type
    key_list = ["data_window", "data_plot"]
    check_data_base.check_dict("data_viewer", data_viewer, key_list=key_list)

    # extract field
    data_window = data_viewer["data_window"]
    data_plot = data_viewer["data_plot"]

    # check window data
    _check_data_window(data_window)

    # check type
    key_list = ["plot_type", "clip_options", "data_options", "plot_options"]
    check_data_base.check_dict("data_plot", data_plot, key_list=key_list)

    # get the data
    plot_type = data_plot["plot_type"]
    clip_options = data_plot["clip_options"]
    data_options = data_plot["data_options"]
    plot_options = data_plot["plot_options"]

    # check plot type
    check_data_base.check_choice("plot_type", plot_type, ["domain", "connection", "voxelization"])

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
    check_data_base.check_list("data_plotter", data_plotter, sub_type=dict)

    # check items
    for data_plotter_tmp in data_plotter:
        _check_data_plotter_item(data_plotter_tmp)


def check_data_viewer(data_viewer):
    """
    Check the type of the data defining several plots.
    This function is used for the viewer.
    """

    # check type
    check_data_base.check_list("data_viewer", data_viewer, sub_type=dict)

    # check items
    for data_viewer_tmp in data_viewer:
        _check_data_viewer_item(data_viewer_tmp)
