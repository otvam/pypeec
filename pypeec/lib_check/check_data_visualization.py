"""
Module for checking the viewer and plotter data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

from pypeec.lib_check import datachecker


def _check_data_window(data_window):
    """
    Check the plot window options (for the viewer and plotter).
    Check the window title, window size, and menu configuration.
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


def _check_data_options(data_options):
    """
    Check the plot options (for the viewer and plotter).
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
    Check the validity of the plot options (for the viewer and plotter).
    The plot options are controlling the 3D wireframe rendering.
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
    Check the validity of the plot theme (for the viewer and plotter).
    The plot options are controlling the 3D plot color and size.
    """

    # check type
    key_list = [
        "text_color", "title_font",
        "colorbar_font", "colorbar_size",
        "background_color", "axis_size",
    ]
    datachecker.check_dict("data_window", plot_theme, key_list=key_list)

    # check data
    datachecker.check_string("text_color", plot_theme["text_color"], can_be_empty=False)
    datachecker.check_string("background_color", plot_theme["background_color"], can_be_empty=False)
    datachecker.check_integer("title_font", plot_theme["title_font"], is_positive=True, can_be_zero=False)
    datachecker.check_integer("colorbar_font", plot_theme["colorbar_font"], is_positive=True, can_be_zero=False)
    datachecker.check_integer("colorbar_size", plot_theme["colorbar_size"], is_positive=True, can_be_zero=False)
    datachecker.check_integer("axis_size", plot_theme["axis_size"], is_positive=True, can_be_zero=False)


def _check_plot_clip(plot_clip):
    """
    Check the validity of the clip options (for the viewer and plotter).
    The clip options are controlling the cut plane (clipping) of the plots.
    """

    # check type
    key_list = ["clip_plot", "clip_invert", "clip_axis", "clip_value"]
    datachecker.check_dict("plot_clip", plot_clip, key_list=key_list)

    # check data
    datachecker.check_boolean("clip_plot", plot_clip["clip_plot"])
    datachecker.check_boolean("clip_invert", plot_clip["clip_invert"])
    datachecker.check_choice("clip_axis", plot_clip["clip_axis"], ["x", "y", "z"])
    datachecker.check_float("clip_value", plot_clip["clip_value"])


def _check_plot_content_plotter_pyvista(plot_type, plot_content):
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
        datachecker.check_dict("plot_content", plot_content, key_list=key_list)

        # check data
        datachecker.check_string("color_electric", plot_content["color_electric"], can_be_empty=False)
        datachecker.check_string("color_magnetic", plot_content["color_magnetic"], can_be_empty=False)
        datachecker.check_string("color_current_source", plot_content["color_current_source"], can_be_empty=False)
        datachecker.check_string("color_voltage_source", plot_content["color_voltage_source"], can_be_empty=False)

    # check the options for scalar and arrow plots
    if plot_type in ["scalar_voxel", "scalar_point", "arrow_voxel", "arrow_point"]:
        # check type
        key_list = ["scale", "log", "legend", "color_lim", "filter_lim"]
        datachecker.check_dict("plot_content", plot_content, key_list=key_list)

        # check data
        datachecker.check_boolean("log", plot_content["log"])
        datachecker.check_string("legend", plot_content["legend"], can_be_empty=False)
        datachecker.check_float("scale", plot_content["scale"], is_positive=True, can_be_zero=True)
        datachecker.check_float_array("color_lim", plot_content["color_lim"], size=2, can_be_none=True)
        datachecker.check_float_array("filter_lim", plot_content["filter_lim"], size=2, can_be_none=True)

    # check the scalar options
    if plot_type in ["scalar_voxel", "scalar_point"]:
        # check type
        key_list = ["var", "point_size"]
        datachecker.check_dict("plot_content", plot_content, key_list=key_list)

        # check data
        datachecker.check_string("var", plot_content["var"], can_be_empty=False)
        datachecker.check_float("point_size", plot_content["point_size"], is_positive=True, can_be_zero=True)

        # check compatibility
        if plot_type == "scalar_voxel":
            datachecker.check_choice("var", plot_content["var"], var_voxel_list)
        elif plot_type == "scalar_point":
            datachecker.check_choice("var", plot_content["var"], var_point_list)
        else:
            raise ValueError("plot_geom: the plot geometry option is incompatible with the plot type")

    # check the arrow options
    if plot_type in ["arrow_voxel", "arrow_point"]:
        # check type
        key_list = ["var_scalar", "var_vector", "arrow_scale", "arrow_threshold"]
        datachecker.check_dict("plot_content", plot_content, key_list=key_list)

        # check data
        datachecker.check_string("var_scalar", plot_content["var_scalar"], can_be_empty=False)
        datachecker.check_string("var_vector", plot_content["var_vector"], can_be_empty=False)
        datachecker.check_float("arrow_scale", plot_content["arrow_scale"], is_positive=True, can_be_zero=True)
        datachecker.check_float("arrow_threshold", plot_content["arrow_threshold"], is_positive=True, can_be_zero=True)

        # check compatibility
        if plot_type == "arrow_voxel":
            datachecker.check_choice("var_scalar", plot_content["var_scalar"], var_voxel_list)
            datachecker.check_choice("var_vector", plot_content["var_vector"], vec_voxel_list)
        elif plot_type == "arrow_point":
            datachecker.check_choice("var_scalar", plot_content["var_scalar"], var_point_list)
            datachecker.check_choice("var_vector", plot_content["var_vector"], vec_point_list)
        else:
            raise ValueError("plot_geom: the plot geometry option is incompatible with the plot type")


def _check_plot_content_plotter_matplotlib(plot_type, plot_content):
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
        key_list = ["color_active", "color_reactive", "marker"]
        datachecker.check_dict("plot_content", plot_content, key_list=key_list)

        # check data
        datachecker.check_string("color_active", plot_content["color_active"], can_be_empty=False)
        datachecker.check_string("color_reactive", plot_content["color_reactive"], can_be_empty=False)
        datachecker.check_string("marker", plot_content["marker"], can_be_empty=False)

    # check the residuum options
    if plot_type == "residuum":
        # check type
        key_list = ["n_bins", "tol_bins", "edge_color", "bar_color"]
        datachecker.check_dict("plot_content", plot_content, key_list=key_list)

        # check data
        datachecker.check_integer("n_bins", plot_content["n_bins"], is_positive=True, can_be_zero=False)
        datachecker.check_float("tol_bins", plot_content["tol_bins"], is_positive=True, can_be_zero=False)
        datachecker.check_string("edge_color", plot_content["edge_color"], can_be_empty=False)
        datachecker.check_string("bar_color", plot_content["bar_color"], can_be_empty=False)


def _check_plot_content_viewer(plot_type, plot_content):
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
        datachecker.check_dict("plot_content", plot_content, key_list=key_list)

        # check data
        datachecker.check_string("color_voxel", plot_content["color_voxel"], can_be_empty=False)
        datachecker.check_string("color_reference", plot_content["color_reference"], can_be_empty=False)
        datachecker.check_float("opacity_voxel", plot_content["opacity_voxel"], is_positive=True, can_be_zero=False)
        datachecker.check_float("opacity_reference", plot_content["opacity_reference"], is_positive=True, can_be_zero=False)

    # check the scalar options
    if plot_type in ["domain", "connection"]:
        # check type
        key_list = ["colormap", "opacity"]
        datachecker.check_dict("plot_content", plot_content, key_list=key_list)

        # check data
        datachecker.check_string("colormap", plot_content["colormap"], can_be_empty=False)
        datachecker.check_float("opacity", plot_content["opacity"], is_positive=True, can_be_zero=False)


def _check_data_plotter_matplotlib(data_plot):
    """
    Check the data describing a Matplotlib plot (for the plotter).
    """

    # check type
    key_list = ["plot_type", "plot_content"]
    datachecker.check_dict("data_plot", data_plot, key_list=key_list)

    # extract the data
    plot_type = data_plot["plot_type"]
    plot_content = data_plot["plot_content"]

    # check plot type
    datachecker.check_choice("plot_type", plot_type, ["convergence", "residuum"])

    # check data
    _check_plot_content_plotter_matplotlib(plot_type, plot_content)


def _check_data_plotter_pyvista(data_plot):
    """
    Check the data describing a PyVista plot (for the plotter).
    """

    # check type
    key_list = ["plot_title", "plot_type", "plot_clip", "plot_content", "plot_view"]
    datachecker.check_dict("data_plot", data_plot, key_list=key_list)

    # extract the data
    plot_title = data_plot["plot_title"]
    plot_type = data_plot["plot_type"]
    plot_content = data_plot["plot_content"]
    plot_clip = data_plot["plot_clip"]
    plot_view = data_plot["plot_view"]
    plot_theme = data_plot["plot_theme"]

    # check plot type
    datachecker.check_choice("plot_type", plot_type, ["material", "scalar_voxel", "scalar_point", "arrow_voxel", "arrow_point"])

    # check title data
    datachecker.check_string("plot_title", plot_title, can_be_empty=False)

    # check data
    _check_plot_content_plotter_pyvista(plot_type, plot_content)
    _check_plot_clip(plot_clip)
    _check_plot_view(plot_view)
    _check_plot_theme(plot_theme)


def _check_data_plotter_item(data_plotter):
    """
    Check the validity of the dict describing a single plot (for the plotter).
    """

    # check type
    key_list = ["plot_framework", "data_window", "data_plot"]
    datachecker.check_dict("data_plotter", data_plotter, key_list=key_list)

    # extract field
    plot_framework = data_plotter["plot_framework"]
    data_window = data_plotter["data_window"]
    data_plot = data_plotter["data_plot"]

    # check plot framework
    datachecker.check_choice("plot_framework", plot_framework, ["matplotlib", "pyvista"])

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
    key_list = ["title", "framework", "data_window", "data_plot", "data_options"]
    datachecker.check_dict("data_viewer", data_viewer, key_list=key_list)

    # extract field
    title = data_viewer["title"]
    data_window = data_viewer["data_window"]
    data_plot = data_viewer["data_plot"]
    data_options = data_viewer["data_options"]

    # check title
    datachecker.check_string("title", title, can_be_empty=False)

    # check window data
    _check_data_window(data_window)

    # check type
    key_list = ["plot_type", "plot_content"]
    datachecker.check_dict("data_plot", data_plot, key_list=key_list)

    # extract the data
    plot_type = data_plot["plot_type"]
    plot_content = data_plot["plot_content"]

    # check plot type
    datachecker.check_choice("plot_type", plot_type, ["domain", "connection", "voxelization"])

    # check options
    _check_plot_content_viewer(plot_type, plot_content)
    _check_data_options(data_options)


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
        _check_data_plotter_item(data_plotter_tmp)


def check_data_viewer(data_viewer):
    """
    Check the type of the data defining several plots.
    This function is used for the viewer.
    """

    # check type
    datachecker.check_dict("data_viewer", data_viewer)

    # check items
    for data_viewer_tmp in data_viewer.values():
        _check_data_viewer_item(data_viewer_tmp)
