"""
Define the options for the viewer and plotter.
Ultimately, these options are dumped into JSON files.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"


def _get_plot_options():
    """
    The plot options are controlling the wireframes and the origin marker.
    This structure is used by the viewer and the plotter.
    """

    plot_options = {
        "grid_plot": True,
        "grid_thickness": 1.0,
        "grid_color": "black",
        "grid_opacity": 0.1,
        "geom_plot": True,
        "geom_thickness": 1.0,
        "geom_color": "black",
        "geom_opacity": 0.5,
        "origin_plot": True,
        "origin_size": 0.1,
        "origin_color": "red",
    }

    return plot_options


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
    This structure is used by the plotter.
    """

    data_options = {
        "plot_legend": name,
        "plot_title": name,
    }

    data = _get_data_plotter_item(name, "material", data_options)

    return data


def _get_data_plotter_scalar(var, scale, unit, name):
    """
    Plot options for a scalar variable (scalar plot).
    This structure is used by the plotter.
    """

    data_options = {
        "var": var,
        "scale": scale,
        "log": False,
        "color_lim": (None, None),
        "filter_lim": (None, None),
        "plot_legend": "%s [%s]" % (name, unit),
        "plot_title": name,
    }

    data = _get_data_plotter_item(name, "scalar", data_options)

    return data


def _get_data_plotter_arrow(var, vec, scale, unit, name):
    """
    Plot options for a vector variable (arrow plot).
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
        "plot_legend": "%s [%s]" % (name, unit),
        "plot_title": name,
    }

    data = _get_data_plotter_item(name, "arrow", data_options)

    return data


def _get_data_plotter_item(name, plot_type, data_options):
    """
    Get the options defining a single plot for the plotter.
    This structure is used by the plotter.
    """

    data = {
        "plot_type": plot_type,
        "data_options": data_options,
        "plot_options": _get_plot_options(),
        "data_window": _get_data_window(name),
    }

    return data


def get_data_viewer():
    """
    Get the options for visualizing the voxel structure.
    This structure is used by the viewer.
    """

    data_viewer = {
        "plot_title": "Viewer",
        "plot_options": _get_plot_options(),
        "data_window": _get_data_window("Viewer"),
    }

    return data_viewer


def get_data_plotter():
    """
    Get the options for plotting the solver solution.
    Each element in the list represent a different plot.
    This structure is used by the plotter.
    """

    data_plotter = [
        _get_data_plotter_geometry("Material"),
        _get_data_plotter_scalar("rho", 1e8, "uOhm/cm", "Resistivity"),
        _get_data_plotter_scalar("V_abs", 1e0, "V", "Potential"),
        _get_data_plotter_scalar("J_norm_abs", 1e-6, "A/mm2", "Current Norm"),
        _get_data_plotter_arrow("J_norm_re", "J_vec_re", 1e-6, "A/mm2", "Re. Current"),
        _get_data_plotter_arrow("J_norm_im", "J_vec_im", 1e-6, "A/mm2", "Im. Current"),
    ]

    return data_plotter
