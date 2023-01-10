"""
Different functions for plotting the solution with PyVista.
The following plots are available:
    - material description (conductors, voltage sources, and current sources)
    - scalar plots (resistivity, potential, and current density)
    - arrow plots (current density)
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np
import pyvista as pv


def _get_plot_base(pl, grid, geom, title, plot_options):
    """
    Plot the geometry as wireframe (complete grid and non-empty voxels).
    Add the axis descriptor to orientate the geometry.
    Add a plot title.
    """

    # plot the complete grid
    if plot_options["grid_plot"]:
        pl.add_mesh(
            grid,
            style="wireframe",
            color=plot_options["grid_color"],
            opacity=plot_options["grid_opacity"],
            line_width=plot_options["grid_thickness"]
        )

    # plot the non-empty voxels
    if plot_options["geom_plot"]:
        pl.add_mesh(
            geom,
            style="wireframe",
            color=plot_options["geom_color"],
            opacity=plot_options["geom_opacity"],
            line_width=plot_options["geom_thickness"]
        )

    # add a marker at the origin
    if plot_options["origin_plot"]:
        # get the marker size
        origin_size = plot_options["origin_size"]
        d = np.min(grid.spacing)
        r = d*origin_size

        # add the marker
        origin = pv.Sphere(r, (0, 0, 0))
        pl.add_mesh(origin, color=plot_options["origin_color"])

    # add title and axes
    pl.add_axes(line_width=2)
    pl.add_text(title, font_size=10)


def _scale_range_vector(geom, var, filter_lim, color_lim, scale):
    """
    Scale a variable and clamp the values between a lower and upper bound.
    """

    # filter data
    geom = geom.threshold(value=filter_lim, scalars=var)

    # convert to numpy
    data = geom[var]
    data = np.array(data)

    # clamp range
    data = np.maximum(data, np.min(color_lim))
    data = np.minimum(data, np.max(color_lim))

    # add scaling
    data = scale*data

    # assign data
    geom[var] = data

    return geom


def plot_material(pl, grid, geom, plot_options, data_options):
    """
    Plot the material description (conductors, voltage sources, and current sources).
    The following encoding is used:
        - 0: conducting voxels
        - 1: current source voxels
        - 2: voltage source voxels
    """

    # copy to avoid a mess with scaling
    grid = grid.copy(deep=True)
    geom = geom.copy(deep=True)

    # extract
    legend = data_options["legend"]
    title = data_options["title"]

    # color bar options (no label as the positions are indicated with annotations)
    scalar_bar_args = dict(
        n_labels=0,
        label_font_size=15,
        title_font_size=15,
        title=legend,
    )

    # get annotations
    annotations = {
        0: "Conductor",
        1: "Current Src.",
        2: "Voltage Src.",
    }

    # get a colormap with three discrete color
    cmap = ["yellow", "green", "blue"]

    # add the resulting plot to the lib_plotter
    pl.add_mesh(
        geom,
        scalars="material",
        scalar_bar_args=scalar_bar_args,
        annotations=annotations,
        cmap=cmap,
    )

    # add the plot background (wireframe, axis, and title)
    _get_plot_base(pl, grid, geom, title, plot_options)


def plot_scalar(pl, grid, geom, plot_options, data_options):
    """
    Plot a scalar variable (resistivity, potential, or current density).
    The variable is plotted on the faces of the voxels.
    """

    # copy to avoid a mess with scaling
    grid = grid.copy(deep=True)
    geom = geom.copy(deep=True)

    # extract
    var = data_options["var"]
    scale = data_options["scale"]
    log = data_options["log"]
    filter_lim = data_options["filter_lim"]
    color_lim = data_options["color_lim"]
    legend = data_options["legend"]
    title = data_options["title"]

    # color bar options
    scalar_bar_args = dict(
        n_labels=5,
        label_font_size=15,
        title_font_size=15,
        title=legend,
    )

    # scale and clamp the variable
    geom = _scale_range_vector(geom, var, filter_lim, color_lim, scale)

    # add the resulting plot to the lib_plotter
    pl.add_mesh(
        geom,
        scalars=var,
        log_scale=log,
        scalar_bar_args=scalar_bar_args,
    )

    # add the plot background (wireframe, axis, and title)
    _get_plot_base(pl, grid, geom, title, plot_options)


def plot_arrow(pl, grid, geom, plot_options, data_options):
    """
    Plot a vector variable (current density) with an arrow plot (quiver plot).
    A scalar variable is used to determine the length and color of the arrows.
    The arrows are located at the center of the voxels.
    """

    # copy to avoid a mess with scaling
    grid = grid.copy(deep=True)
    geom = geom.copy(deep=True)

    # extract
    var = data_options["var"]
    vec = data_options["vec"]
    scale = data_options["scale"]
    arrow = data_options["arrow"]
    log = data_options["log"]
    filter_lim = data_options["filter_lim"]
    color_lim = data_options["color_lim"]
    legend = data_options["legend"]
    title = data_options["title"]

    # color bar options
    scalar_bar_args = dict(
        n_labels=5,
        label_font_size=15,
        title_font_size=15,
        title=legend,
    )

    # scale and clamp the variable
    geom = _scale_range_vector(geom, var, filter_lim, color_lim, scale)

    # get arrow size
    d = np.min(grid.spacing)
    factor = d*arrow

    # create the arrows
    glyphs = geom.glyph(orient=vec, scale=False, factor=factor)

    # add the resulting plot to the lib_plotter
    pl.add_mesh(
        glyphs,
        scalars=var,
        log_scale=log,
        scalar_bar_args=scalar_bar_args,
    )

    # add the plot background (wireframe, axis, and title)
    _get_plot_base(pl, grid, geom, title, plot_options)
