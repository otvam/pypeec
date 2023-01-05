def __get_data_sub(name, plot_type, data_options):
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

    return  data


def __get_geometry(name):
    data_options = {
        "legend": name,
        "title": name,
    }

    data = __get_data_sub(name, "material", data_options)

    return data


def __get_scalar(data, scale, unit, name):
    data_options = {
        "data": data,
        "scale": scale,
        "log": False,
        "lim": [-float("inf"), +float("inf")],
        "legend": "%s [%s]" % (name, unit),
        "title": name,
    }

    data = __get_data_sub(name, "scalar", data_options)

    return data


def __get_arrow(data_norm, data_vec, scale, arrow, unit, name):
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

    data = __get_data_sub(name, "arrow", data_options)

    return data


def get_data():
    data_plotter = [
        __get_geometry("Material"),
        # __get_scalar("rho", 1e8, "uOhm/cm", "Resistivity"),
        # __get_scalar("V_abs", 1e0, "V", "Potential"),
        # __get_scalar("J_norm_abs", 1e-6, "A/mm2", "Current Norm"),
        # __get_arrow("J_norm_re", "J_vec_re", 1e-6, 1e-6, "A/mm2", "Re. Current"),
        # __get_arrow("J_norm_im", "J_vec_im", 1e-6, 1e-6, "A/mm2", "Im. Current"),
    ]

    return data_plotter
