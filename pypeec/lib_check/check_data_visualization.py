"""
Module for checking the viewer and plotter data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

from pypeec.lib_check import datachecker


def _check_data_window(data_window):
    """
    Check the plot window options (for the viewer and plotter).
    Check the window size and menu configuration.
    """

    # check type
    key_list = ["show_menu", "image_size", "window_size", "notebook_size"]
    datachecker.check_dict("data_window", data_window, key_list=key_list)

    # extract the data
    show_menu = data_window["show_menu"]
    image_size = data_window["image_size"]
    window_size = data_window["window_size"]
    notebook_size = data_window["notebook_size"]

    # check data
    datachecker.check_boolean("show_menu", show_menu)
    datachecker.check_integer_array("image_size", image_size, size=2, is_positive=True, can_be_zero=False, can_be_none=True)
    datachecker.check_integer_array("window_size", window_size, size=2, is_positive=True, can_be_zero=False, can_be_none=True)
    datachecker.check_integer_array("notebook_size", notebook_size, size=2, is_positive=True, can_be_zero=False, can_be_none=True)


def _check_data_options_matplotlib(data_options):
    """
    Check the plot options (for Matplotlib).
    """

    # check type
    key_list = ["style", "legend", "font"]
    datachecker.check_dict("data_options", data_options, key_list=key_list)

    # extract the data
    style = data_options["style"]
    legend = data_options["legend"]
    font = data_options["font"]

    # check data
    datachecker.check_string("style", style, can_be_empty=False)
    datachecker.check_string("legend", legend, can_be_empty=False)
    datachecker.check_integer("font", font, is_positive=True, can_be_zero=False)


def _check_data_options_pyvista(data_options):
    """
    Check the plot options (for PyVista).
    """

    # check type
    key_list = ["plot_clip", "plot_view", "plot_theme"]
    datachecker.check_dict("data_options", data_options, key_list=key_list)

    # extract the data
    plot_clip = data_options["plot_clip"]
    plot_view = data_options["plot_view"]
    plot_theme = data_options["plot_theme"]

    _check_plot_clip(plot_clip)
    _check_plot_view(plot_view)
    _check_plot_theme(plot_theme)


def _check_plot_view(plot_view):
    """
    Check the validity of the plot view (for PyVista).
    """

    # check type
    key_list = [
        "grid_plot", "grid_thickness", "grid_color", "grid_opacity",
        "geom_plot", "geom_thickness", "geom_color", "geom_opacity",
        "point_plot", "point_size", "point_color", "point_opacity",
        "camera_roll", "camera_azimuth", "camera_elevation",
    ]
    datachecker.check_dict("data_window", plot_view, key_list=key_list)

    # check grid data
    datachecker.check_boolean("grid_plot", plot_view["grid_plot"])
    datachecker.check_string("grid_color", plot_view["grid_color"], can_be_empty=False)
    datachecker.check_float("grid_thickness", plot_view["grid_thickness"], is_positive=True, can_be_zero=True)
    datachecker.check_float("grid_opacity", plot_view["grid_opacity"], is_positive=True, can_be_zero=True)

    # check geom data
    datachecker.check_boolean("geom_plot", plot_view["geom_plot"])
    datachecker.check_string("geom_color", plot_view["geom_color"], can_be_empty=False)
    datachecker.check_float("geom_thickness", plot_view["geom_thickness"], is_positive=True, can_be_zero=True)
    datachecker.check_float("geom_opacity", plot_view["geom_opacity"], is_positive=True, can_be_zero=True)

    # check cloud data
    datachecker.check_boolean("point_plot", plot_view["point_plot"])
    datachecker.check_string("point_color", plot_view["point_color"], can_be_empty=False)
    datachecker.check_float("point_size", plot_view["point_size"], is_positive=True, can_be_zero=True)
    datachecker.check_float("point_opacity", plot_view["point_opacity"], is_positive=True, can_be_zero=True)

    # check camera data
    datachecker.check_float("camera_roll", plot_view["camera_roll"], can_be_none=True)
    datachecker.check_float("camera_azimuth", plot_view["camera_azimuth"], can_be_none=True)
    datachecker.check_float("camera_elevation", plot_view["camera_elevation"], can_be_none=True)


def _check_plot_theme(plot_theme):
    """
    Check the validity of the plot theme (for PyVista).
    """

    # check type
    key_list = [
        "text_color", "title_font",
        "colorbar_font", "colorbar_size",
        "axis_add", "axis_size",
        "background_color",
    ]
    datachecker.check_dict("data_window", plot_theme, key_list=key_list)

    # check data
    datachecker.check_boolean("axis_add", plot_theme["axis_add"])
    datachecker.check_string("text_color", plot_theme["text_color"], can_be_empty=False)
    datachecker.check_string("background_color", plot_theme["background_color"], can_be_empty=False)
    datachecker.check_integer("title_font", plot_theme["title_font"], is_positive=True, can_be_zero=False)
    datachecker.check_integer("colorbar_font", plot_theme["colorbar_font"], is_positive=True, can_be_zero=False)
    datachecker.check_integer("colorbar_size", plot_theme["colorbar_size"], is_positive=True, can_be_zero=False)
    datachecker.check_integer("axis_size", plot_theme["axis_size"], is_positive=True, can_be_zero=False)


def _check_plot_clip(plot_clip):
    """
    Check the validity of the plot cut plane (for PyVista).
    """

    # check type
    key_list = ["clip_plot", "clip_invert", "clip_axis", "clip_value"]
    datachecker.check_dict("plot_clip", plot_clip, key_list=key_list)

    # check data
    datachecker.check_boolean("clip_plot", plot_clip["clip_plot"])
    datachecker.check_boolean("clip_invert", plot_clip["clip_invert"])
    datachecker.check_choice("clip_axis", plot_clip["clip_axis"], ["x", "y", "z"])
    datachecker.check_float("clip_value", plot_clip["clip_value"])


def _check_data_plot_plotter(layout, data_plot):
    """
    Check the validity of the data options (for the plotter).
    The data options are controlling the plot content.
    """

    # list of allowed plot types
    layout_list = [
        "convergence",
        "residuum",
        "material",
        "scalar_voxel",
        "scalar_point",
        "arrow_voxel",
        "arrow_point",
    ]

    # list of allowed variable names
    var_voxel_list = [
        "V_c_re", "V_c_im", "V_c_abs",
        "V_m_re", "V_m_im", "V_m_abs",
        "S_c_re", "S_c_im", "S_c_abs",
        "Q_m_re", "Q_m_im", "Q_m_abs",
        "J_c_norm", "B_m_norm",
        "P_c_abs", "P_m_abs",
    ]
    var_point_list = ["H_norm"]
    vec_point_list = ["H_vec"]
    vec_voxel_list = ["J_c_vec", "B_m_vec"]

    # check plot type
    datachecker.check_choice("layout", layout, layout_list)

    # check the convergence options
    if layout == "convergence":
        # check type
        key_list = ["color_active", "color_reactive", "marker"]
        datachecker.check_dict("data_plot", data_plot, key_list=key_list)

        # check data
        datachecker.check_string("color_active", data_plot["color_active"], can_be_empty=False)
        datachecker.check_string("color_reactive", data_plot["color_reactive"], can_be_empty=False)
        datachecker.check_float("marker", data_plot["marker"], is_positive=True, can_be_zero=False)
        datachecker.check_float("width", data_plot["width"], is_positive=True, can_be_zero=False)

    # check the residuum options
    if layout == "residuum":
        # check type
        key_list = ["n_bins", "tol_bins", "edge_color", "bar_color"]
        datachecker.check_dict("data_plot", data_plot, key_list=key_list)

        # check data
        datachecker.check_integer("n_bins", data_plot["n_bins"], is_positive=True, can_be_zero=False)
        datachecker.check_float("tol_bins", data_plot["tol_bins"], is_positive=True, can_be_zero=False)
        datachecker.check_string("edge_color", data_plot["edge_color"], can_be_empty=False)
        datachecker.check_string("bar_color", data_plot["bar_color"], can_be_empty=False)

    # check the material options
    if layout == "material":
        # check type
        key_list = ["title", "color_electric", "color_magnetic", "color_current_source", "color_voltage_source"]
        datachecker.check_dict("data_plot", data_plot, key_list=key_list)

        # check data
        datachecker.check_string("title", data_plot["title"], can_be_empty=True)
        datachecker.check_string("color_electric", data_plot["color_electric"], can_be_empty=False)
        datachecker.check_string("color_magnetic", data_plot["color_magnetic"], can_be_empty=False)
        datachecker.check_string("color_current_source", data_plot["color_current_source"], can_be_empty=False)
        datachecker.check_string("color_voltage_source", data_plot["color_voltage_source"], can_be_empty=False)

    # check the options for scalar and arrow plots
    if layout in ["scalar_voxel", "scalar_point", "arrow_voxel", "arrow_point"]:
        # check type
        key_list = ["title", "scale", "log", "legend", "color_lim", "filter_lim"]
        datachecker.check_dict("data_plot", data_plot, key_list=key_list)

        # check data
        datachecker.check_boolean("log", data_plot["log"])
        datachecker.check_string("title", data_plot["title"], can_be_empty=True)
        datachecker.check_string("legend", data_plot["legend"], can_be_empty=True)
        datachecker.check_float("scale", data_plot["scale"], is_positive=True, can_be_zero=True)
        datachecker.check_float_array("color_lim", data_plot["color_lim"], size=2, can_be_none=True)
        datachecker.check_float_array("filter_lim", data_plot["filter_lim"], size=2, can_be_none=True)

    # check the scalar options
    if layout in ["scalar_voxel", "scalar_point"]:
        # check type
        key_list = ["var", "point_size"]
        datachecker.check_dict("data_plot", data_plot, key_list=key_list)

        # check data
        datachecker.check_string("var", data_plot["var"], can_be_empty=False)
        datachecker.check_float("point_size", data_plot["point_size"], is_positive=True, can_be_zero=True)

        # check compatibility
        if layout == "scalar_voxel":
            datachecker.check_choice("var", data_plot["var"], var_voxel_list)
        elif layout == "scalar_point":
            datachecker.check_choice("var", data_plot["var"], var_point_list)
        else:
            raise ValueError("plot_geom: the plot geometry option is incompatible with the plot type")

    # check the arrow options
    if layout in ["arrow_voxel", "arrow_point"]:
        # check type
        key_list = ["var", "phase", "arrow_scale", "arrow_threshold"]
        datachecker.check_dict("data_plot", data_plot, key_list=key_list)

        # check data
        datachecker.check_float("phase", data_plot["phase"])
        datachecker.check_string("var", data_plot["var"], can_be_empty=False)
        datachecker.check_float("arrow_scale", data_plot["arrow_scale"], is_positive=True, can_be_zero=True)
        datachecker.check_float("arrow_threshold", data_plot["arrow_threshold"], is_positive=True, can_be_zero=True)

        # check compatibility
        if layout == "arrow_voxel":
            datachecker.check_choice("var", data_plot["var"], vec_voxel_list)
        elif layout == "arrow_point":
            datachecker.check_choice("var", data_plot["var"], vec_point_list)
        else:
            raise ValueError("plot_geom: the plot geometry option is incompatible with the plot type")


def _check_data_plot_viewer(layout, data_plot):
    """
    Check the validity of the data options (for the viewer).
    The data options are controlling the plot content.
    """

    # check plot type
    datachecker.check_choice("layout", layout, ["domain", "connection", "voxelization"])

    # check the material options
    if layout == "voxelization":
        # check type
        key_list = ["color_voxel", "color_reference", "opacity_voxel", "opacity_reference"]
        datachecker.check_dict("data_plot", data_plot, key_list=key_list)

        # check data
        datachecker.check_string("title", data_plot["title"], can_be_empty=True)
        datachecker.check_string("color_voxel", data_plot["color_voxel"], can_be_empty=False)
        datachecker.check_string("color_reference", data_plot["color_reference"], can_be_empty=False)
        datachecker.check_float("opacity_voxel", data_plot["opacity_voxel"], is_positive=True, can_be_zero=False)
        datachecker.check_float("opacity_reference", data_plot["opacity_reference"], is_positive=True, can_be_zero=False)

    # check the scalar options
    if layout in ["domain", "connection"]:
        # check type
        key_list = ["colormap", "title", "opacity"]
        datachecker.check_dict("data_plot", data_plot, key_list=key_list)

        # check data
        datachecker.check_string("colormap", data_plot["colormap"], can_be_empty=False)
        datachecker.check_string("title", data_plot["title"], can_be_empty=True, can_be_none=True)
        datachecker.check_float("opacity", data_plot["opacity"], is_positive=True, can_be_zero=False)


def _check_data_item(data_item, handler):
    """
    Check the validity of the dict describing a single plot (for the viewer and plotter).
    """

    # check type
    key_list = ["title", "framework", "layout", "data_window", "data_plot", "data_options"]
    datachecker.check_dict("data_item", data_item, key_list=key_list)

    # extract field
    framework = data_item["framework"]
    title = data_item["title"]
    layout = data_item["layout"]
    data_window = data_item["data_window"]
    data_plot = data_item["data_plot"]
    data_options = data_item["data_options"]

    # check plot framework
    datachecker.check_choice("framework", framework, ["matplotlib", "pyvista"])

    # check title
    datachecker.check_string("title", title, can_be_empty=False)

    # check window data
    _check_data_window(data_window)

    # check options
    if framework == "pyvista":
        _check_data_options_pyvista(data_options)
    elif framework == "matplotlib":
        _check_data_options_matplotlib(data_options)
    else:
        raise ValueError("invalid plot framework")

    # check content
    if handler == "plotter":
        _check_data_plot_plotter(layout, data_plot)
    elif handler == "viewer":
        _check_data_plot_viewer(layout, data_plot)
    else:
        raise ValueError("invalid plot framework")


def check_data_point(data_point):
    """
    Check the point structure (defining the point cloud).
    The point cloud is used for magnetic field evaluation.
    """

    # check type
    datachecker.check_float_pts("data_point", data_point, size=3, can_be_empty=True)


def check_data_plotter(data_plotter):
    """
    Check the type of the data defining several plots.
    This function is used for the plotter.
    """

    # check type
    datachecker.check_dict("data_plotter", data_plotter)

    # check items
    for data_plotter_tmp in data_plotter.values():
        _check_data_item(data_plotter_tmp, "plotter")


def check_data_viewer(data_viewer):
    """
    Check the type of the data defining several plots.
    This function is used for the viewer.
    """

    # check type
    datachecker.check_dict("data_viewer", data_viewer)

    # check items
    for data_viewer_tmp in data_viewer.values():
        _check_data_item(data_viewer_tmp, "viewer")
