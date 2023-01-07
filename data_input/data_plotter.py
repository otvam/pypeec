def _get_data_sub(name, plot_type, data_options):
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

    data = {
        "title": name,
        "plot_type": plot_type,
        "window_size": (800, 600),
        "data_options": data_options,
        "plot_options": plot_options
    }

    return data


def _get_geometry(name):
    data_options = {
        "legend": name,
        "title": name,
    }

    data = _get_data_sub(name, "material", data_options)

    return data


def _get_scalar(var, scale, unit, name):
    data_options = {
        "var": var,
        "scale": scale,
        "log": False,
        "color_lim": [-float("inf"), +float("inf")],
        "filter_lim": [-float("inf"), +float("inf")],
        "legend": "%s [%s]" % (name, unit),
        "title": name,
    }

    data = _get_data_sub(name, "scalar", data_options)

    return data


def _get_arrow(var, vec, scale, arrow, unit, name):
    data_options = {
        "var": var,
        "vec": vec,
        "scale": scale,
        "arrow": arrow,
        "log": False,
        "color_lim": [-float("inf"), +float("inf")],
        "filter_lim": [-float("inf"), +float("inf")],
        "legend": "%s [%s]" % (name, unit),
        "title": name,
    }

    data = _get_data_sub(name, "arrow", data_options)

    return data


def get_data():
    data_plotter = [
        _get_geometry("Material"),
        _get_scalar("rho", 1e8, "uOhm/cm", "Resistivity"),
        _get_scalar("V_abs", 1e0, "V", "Potential"),
        _get_scalar("J_norm_abs", 1e-6, "A/mm2", "Current Norm"),
        _get_arrow("J_norm_re", "J_vec_unit_re", 1e-6, 2e-5, "A/mm2", "Re. Current"),
        _get_arrow("J_norm_im", "J_vec_unit_im", 1e-6, 2e-5, "A/mm2", "Im. Current"),
    ]

    return data_plotter
