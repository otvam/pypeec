import numpy as np


def __get_plot_base(pl, grid, geom, plot_options):
    if plot_options["grid_plot"]:
        pl.add_mesh(
            grid,
            style='wireframe',
            color=plot_options["grid_color"],
            opacity=plot_options["grid_opacity"],
            line_width=plot_options["grid_thickness"]
        )
    if plot_options["geom_plot"]:
        pl.add_mesh(
            geom,
            style='wireframe',
            color=plot_options["geom_color"],
            opacity=plot_options["geom_opacity"],
            line_width=plot_options["geom_thickness"]
        )

    pl.add_axes(line_width=5)


def __scale_range_vector(data, scale, range):
    # convert to numpy
    data = np.array(data)

    # add scaling
    data = scale*data

    # clamp range
    data = np.maximum(data, np.min(range))
    data = np.minimum(data, np.max(range))

    return data


def plot_material(pl, grid, geom, plot_options, data_options):
    # copy to avoid a mess with scaling
    grid = grid.copy(deep=True)
    geom = geom.copy(deep=True)

    # extract
    legend = data_options["legend"]
    title = data_options["title"]

    # color bar options
    scalar_bar_args = dict(
        n_labels=0,
        label_font_size=15,
        title_font_size=15,
        title=legend,
    )

    # get annotations
    annotations = {
        0: 'Conductor',
        1: 'Current Src.',
        2: 'Voltage Src.',
    }

    # get colormap
    cmap = ['yellow', 'red', 'blue']

    # add the payload
    pl.add_mesh(
        geom,
        scalars="material",
        scalar_bar_args=scalar_bar_args,
        annotations=annotations,
        cmap=cmap,
    )

    # add the plot background
    __get_plot_base(pl, grid, geom, plot_options)

    pl.add_text(title, font_size=10)


def plot_scalar(pl, grid, geom, plot_options, data_options):
    # copy to avoid a mess with scaling
    grid = grid.copy(deep=True)
    geom = geom.copy(deep=True)

    # extract
    data = data_options["data"]
    scale = data_options["scale"]
    log = data_options["log"]
    lim = data_options["lim"]
    legend = data_options["legend"]
    title = data_options["title"]

    # color bar options
    scalar_bar_args = dict(
        n_labels=5,
        label_font_size=15,
        title_font_size=15,
        title=legend,
    )

    # add scaled field
    geom[data] = __scale_range_vector(geom[data], scale, lim)

    # add the payload
    pl.add_mesh(
        geom,
        scalars=data,
        log_scale=log,
        scalar_bar_args=scalar_bar_args,
    )

    # add the plot background
    __get_plot_base(pl, grid, geom, plot_options)

    pl.add_text(title, font_size=10)


def plot_arrow(pl, grid, geom, plot_options, data_options):
    # copy to avoid a mess with scaling
    grid = grid.copy(deep=True)
    geom = geom.copy(deep=True)

    # extract
    data_norm = data_options["data_norm"]
    data_vec = data_options["data_vec"]
    scale = data_options["scale"]
    arrow = data_options["arrow"]
    log = data_options["log"]
    lim = data_options["lim"]
    legend = data_options["legend"]
    title = data_options["title"]

    # color bar options
    scalar_bar_args = dict(
        n_labels=5,
        label_font_size=15,
        title_font_size=15,
        title=legend,
    )

    # add scaled field
    geom[data_norm] = __scale_range_vector(geom[data_norm], scale, lim)

    # create the arrows
    glyphs = geom.glyph(orient=data_vec, scale=data_norm, factor=arrow)

    # add the payload
    pl.add_mesh(
        glyphs,
        log_scale=log,
        scalar_bar_args=scalar_bar_args,
    )

    # add the plot background
    __get_plot_base(pl, grid, geom, plot_options)

    pl.add_text(title, font_size=10)

