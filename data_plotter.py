def __get_plot_options():
    plot_options = {
        "grid_plot": True,
        "grid_thickness": 1.0,
        "grid_color": "black",
        "grid_opacity": 0.1,
        "geom_plot": True,
        "geom_thickness": 1.0,
        "geom_color": "black",
        "geom_opacity": 0.5,
    }

    return plot_options


def __get_geometry():
    plot_options = __get_plot_options()
    data_options = {
        "legend": "Material Type",
        "title": "Material",
    }

    data = {
        "title": "Material",
        "window_size": (800, 600),
        "plot_type": "material",
        "data_options": data_options,
        "plot_options": plot_options
    }

    return data


def __get_scalar(data, scale, unit, name):
    plot_options = __get_plot_options()
    data_options = {
        "data": data,
        "scale": scale,
        "log": False,
        "lim": [-float("inf"), +float("inf")],
        "legend": "%s [%s]" % (name, unit),
        "title": name,
    }

    data = {
        "title": name,
        "window_size": (800, 600),
        "plot_type": "scalar",
        "data_options": data_options,
        "plot_options": plot_options
    }

    return data


def __get_arrow(data_norm, data_vec, scale, arrow, unit, name):
    plot_options = __get_plot_options()
    data_options = {
        "data_norm": data_norm,
        "data_vec": data_vec,
        "scale": scale,
        "arrow": arrow,
        "log": False,
        "lim": [-float("inf"), +float("inf")],
        "legend": "%s [%s]" % (name, unit),
        "title": name,
    }

    data = {
        "title": name,
        "window_size": (800, 600),
        "plot_type": "arrow",
        "data_options": data_options,
        "plot_options": plot_options
    }

    return data


def get_data_plotter():
    data_plotter = [
        __get_geometry(),
        __get_scalar("rho", 1e8, "uOhm/cm", "Resistivity"),
        __get_scalar("V_abs", 1e0, "V", "Potential"),
        __get_scalar("J_norm_abs", 1e-6, "A/mm2", "Current Norm"),
        __get_arrow("J_norm_re", "J_vec_re", 1e-6, 1e-6, "A/mm2", "Im. Current"),
        __get_arrow("J_norm_im", "J_vec_im", 1e-6, 1e-6, "A/mm2", "Re. Current"),
    ]

    return data_plotter
