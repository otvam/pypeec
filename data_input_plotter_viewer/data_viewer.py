def get_data():
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

    data_viewer = {
        "window_title": "viewer",
        "plot_title": "viewer",
        "window_size": (800, 600),
        "plot_options": plot_options
    }

    return data_viewer
