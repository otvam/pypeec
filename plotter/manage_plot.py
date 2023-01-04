import numpy as np


def get_plot_base(pl, grid, geom, plot_options):
    if plot_options["grid_plot"]:
        pl.add_mesh(
            grid,
            style='wireframe',
            color="black",
            opacity=plot_options["grid_opacity"],
            line_width=plot_options["grid_thickness"]
        )
    if plot_options["geom_plot"]:
        pl.add_mesh(
            geom,
            style='wireframe',
            color="black",
            opacity=plot_options["geom_opacity"],
            line_width=plot_options["geom_thickness"]
        )

    pl.add_axes(line_width=5)


def plot_geom(pl, grid, geom, plot_options, data_options):
    # extract
    legend = data_options["legend"]
    title = data_options["title"]

    # colorbar options
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

    #get colormap
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
    get_plot_base(pl, grid, geom, plot_options)

    pl.add_text(title, font_size=10)


def plot_scalar(pl, grid, geom, plot_options, data_options):
    # extract
    data = data_options["data"]
    scale = data_options["scale"]
    log = data_options["log"]
    legend = data_options["legend"]
    title = data_options["title"]

    # colorbar options
    scalar_bar_args = dict(
        n_labels=5,
        label_font_size=15,
        title_font_size=15,
        title=legend,
    )

    # add scaled field
    geom["tmp_scale"] = scale*geom[data]

    # add the payload
    pl.add_mesh(
        geom,
        scalars="tmp_scale",
        log_scale=log,
        scalar_bar_args=scalar_bar_args,
    )

    # add the plot background
    get_plot_base(pl, grid, geom, plot_options)

    pl.add_text(title, font_size=10)


def plot_arrow(pl, grid, geom, plot_options, data_options):
    # extract
    data_norm = data_options["data_norm"]
    data_vec = data_options["data_vec"]
    scale = data_options["scale"]
    arrow = data_options["arrow"]
    log = data_options["log"]
    legend = data_options["legend"]
    title = data_options["title"]

    # colorbar options
    scalar_bar_args = dict(
        n_labels=5,
        label_font_size=15,
        title_font_size=15,
        title=legend,
    )

    # add scaled field
    geom["tmp_norm_scale"] = scale*geom[data_norm]
    geom["tmp_vec_scale"] = scale*geom[data_vec]

    # create the arrows
    glyphs = geom.glyph(orient="tmp_vec_scale", scale="tmp_norm_scale", factor=arrow)

    # add the payload
    pl.add_mesh(
        glyphs,
        log_scale=log,
        scalar_bar_args=scalar_bar_args,
    )

    # add the plot background
    get_plot_base(pl, grid, geom, plot_options)

    pl.add_text(title, font_size=10)

