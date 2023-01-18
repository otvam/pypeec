"""
Define the options for the viewer and plotter.
Ultimately, these options are dumped into JSON files.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"


def _get_plot_options(name):
    """
    The plot options are controlling the wireframe rendering.
    This structure is used by the viewer and the plotter.
    """

    plot_options = {
        "title": name,
        "grid_plot": True,
        "grid_thickness": 1.0,
        "grid_color": "black",
        "grid_opacity": 0.1,
        "geom_plot": True,
        "geom_thickness": 1.0,
        "geom_color": "black",
        "geom_opacity": 0.5,
        "cloud_plot": True,
        "cloud_color": "black",
        "cloud_size": 5.0,
        "cloud_opacity": 0.5,
    }

    return plot_options


def _get_clip_options():
    """
    Define the display (with/without clipping plane).
    """

    clip_options = {
        "clip_plot": False,
        "clip_invert": False,
        "clip_axis": "x",
        "clip_value": 0.0,
    }

    return clip_options


def _get_data_window(name):
    """
    The window options are the window title and appearance.
    This structure is used by the viewer and the plotter.
    """

    data_window = {
        "title": name,
        "show_menu": False,
        "size": (800, 600),
    }

    return data_window


def _get_data_plotter_geometry(name):
    """
    Plot options for the material description (conductors and sources).
    The result is plotted on the voxel structure.
    This structure is used by the plotter.
    """

    data_options = {
        "legend": name,
        "opacity": 1.0,
    }

    data = _get_data_plotter_item("material", "material", name, data_options)

    return data


def _get_data_plotter_scalar(plot_geom, var, scale, unit, name):
    """
    Plot options for a scalar variable (scalar plot).
    The variable is either plotted on the voxel structure or on a provided point cloud.
    This structure is used by the plotter.
    """

    data_options = {
        "var": var,
        "scale": scale,
        "log": False,
        "color_lim": (None, None),
        "filter_lim": (None, None),
        "opacity": 1.0,
        "size": 10.0,
        "legend": "%s [%s]" % (name, unit),
    }

    data = _get_data_plotter_item("scalar", plot_geom, name, data_options)

    return data


def _get_data_plotter_arrow(plot_geom, var, vec, scale, unit, name):
    """
    Plot options for a vector variable (arrow plot).
    The variable is either plotted on the voxel structure or on a provided point cloud.
    This structure is used by the plotter.
    """

    data_options = {
        "var": var,
        "vec": vec,
        "scale": scale,
        "log": False,
        "color_lim": (None, None),
        "filter_lim": (None, None),
        "arrow_threshold": 1e-3,
        "arrow_scale": 0.5,
        "legend": "%s [%s]" % (name, unit),
    }

    data = _get_data_plotter_item("arrow", plot_geom, name, data_options)

    return data


def _get_data_plotter_item(plot_type, plot_geom, name, data_options):
    """
    Get the options defining a single plot for the plotter.
    This structure is used by the plotter.
    """

    data = {
        "plot_type": plot_type,
        "plot_geom": plot_geom,
        "data_options": data_options,
        "clip_options": _get_clip_options(),
        "plot_options": _get_plot_options(name),
        "data_window": _get_data_window(name),
    }

    return data


def get_data_viewer():
    """
    Get the options for visualizing the voxel structure.
    Each element in the list represents a different plot.
    This structure is used by the viewer.
    """

    data_viewer = [
        {
            "plot_type": "domain",
            "clip_options": _get_clip_options(),
            "plot_options": _get_plot_options("Domain"),
            "data_window": _get_data_window("Domain"),
        },
        {
            "plot_type": "graph",
            "clip_options": _get_clip_options(),
            "plot_options": _get_plot_options("Graph"),
            "data_window": _get_data_window("Graph"),
        },
    ]

    return data_viewer


def get_data_plotter():
    """
    Get the options for plotting the solver solution.
    Each element in the list represents a different plot.
    This structure is used by the plotter.
    """

    data_plotter = [
        _get_data_plotter_geometry("Material"),
        _get_data_plotter_scalar("voxel", "rho", 1e8, "uOhm/cm", "Resistivity"),
        _get_data_plotter_scalar("voxel", "V_abs", 1e0, "V", "Potential"),
        _get_data_plotter_scalar("voxel", "J_norm_abs", 1e-6, "A/mm2", "Current Norm"),
        _get_data_plotter_arrow("voxel", "J_norm_re", "J_vec_re", 1e-6, "A/mm2", "Re. Current"),
        _get_data_plotter_arrow("voxel", "J_norm_im", "J_vec_im", 1e-6, "A/mm2", "Im. Current"),
        _get_data_plotter_scalar("point", "H_norm_abs", 1e0, "A/m", "Mag. Field Norm"),
        _get_data_plotter_arrow("point", "H_norm_re", "H_vec_re", 1e0, "A/m", "Re. Mag. Field"),
        _get_data_plotter_arrow("point", "H_norm_im", "H_vec_im", 1e0, "A/m", "Im. Mag. Field"),
    ]

    return data_plotter
