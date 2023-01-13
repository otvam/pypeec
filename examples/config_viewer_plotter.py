import json


def _get_plot_options():
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


def _get_data_plotter_geometry(name):
    data_options = {
        "plot_legend": name,
        "plot_title": name,
    }

    data = _get_data_plotter_item(name, "material", data_options)

    return data


def _get_data_plotter_scalar(var, scale, unit, name):
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
    plot_options = _get_plot_options()

    data = {
        "window_title": name,
        "plot_type": plot_type,
        "window_size": (800, 600),
        "data_options": data_options,
        "plot_options": plot_options,
    }

    return data


def get_data_viewer():
    plot_options = _get_plot_options()

    data_viewer = {
        "window_title": "Viewer",
        "plot_title": "Viewer",
        "window_size": (800, 600),
        "plot_options": plot_options,
    }

    return data_viewer


def get_data_plotter():
    data_plotter = [
        _get_data_plotter_geometry("Material"),
        _get_data_plotter_scalar("rho", 1e8, "uOhm/cm", "Resistivity"),
        _get_data_plotter_scalar("V_abs", 1e0, "V", "Potential"),
        _get_data_plotter_scalar("J_norm_abs", 1e-6, "A/mm2", "Current Norm"),
        _get_data_plotter_arrow("J_norm_re", "J_vec_re", 1e-6, "A/mm2", "Re. Current"),
        _get_data_plotter_arrow("J_norm_im", "J_vec_im", 1e-6, "A/mm2", "Im. Current"),
    ]

    return data_plotter
