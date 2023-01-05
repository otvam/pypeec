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


def __get_plot_base(pl, grid, geom, title, plot_options):
    """
    Plot the geometry as wireframe (complete grid and non-empty voxels).
    Add the axis descriptor to orientate the geometry.
    Add a plot title.
    """

    # plot the complete grid
    if plot_options["grid_plot"]:
        pl.add_mesh(
            grid,
            style='wireframe',
            color=plot_options["grid_color"],
            opacity=plot_options["grid_opacity"],
            line_width=plot_options["grid_thickness"]
        )

    # plot the non-empty voxels
    if plot_options["geom_plot"]:
        pl.add_mesh(
            geom,
            style='wireframe',
            color=plot_options["geom_color"],
            opacity=plot_options["geom_opacity"],
            line_width=plot_options["geom_thickness"]
        )

    # add a marker at the origin
    if plot_options["origin_plot"]:
        d = np.min(grid.spacing)
        r = d*plot_options["origin_size"]
        origin = pv.Sphere(r, (0, 0, 0))
        pl.add_mesh(origin, color=plot_options["origin_color"])

    # add title and axes
    pl.add_axes(line_width=2)
    pl.add_text(title, font_size=10)


def __scale_range_vector(data, scale, lim):
    """
    Scale a variable and clamp the values between a lower and upper bound.
    """

    # convert to numpy
    data = np.array(data)

    # add scaling
    data = scale*data

    # clamp range
    data = np.maximum(data, np.min(lim))
    data = np.minimum(data, np.max(lim))

    return data


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
        0: 'Conductor',
        1: 'Current Src.',
        2: 'Voltage Src.',
    }

    # get a colormap with three discrete color
    cmap = ['yellow', 'green', 'blue']

    # add the resulting plot to the plotter
    pl.add_mesh(
        geom,
        scalars="material",
        scalar_bar_args=scalar_bar_args,
        annotations=annotations,
        cmap=cmap,
    )

    # add the plot background (wireframe, axis, and title)
    __get_plot_base(pl, grid, geom, title, plot_options)


def plot_scalar(pl, grid, geom, plot_options, data_options):
    """
    Plot a scalar variable (resistivity, potential, or current density).
    The variable is plotted on the faces of the voxels.
    """

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

    # scale and clamp the variable
    geom[data] = __scale_range_vector(geom[data], scale, lim)

    # add the resulting plot to the plotter
    pl.add_mesh(
        geom,
        scalars=data,
        log_scale=log,
        scalar_bar_args=scalar_bar_args,
    )

    # add the plot background (wireframe, axis, and title)
    __get_plot_base(pl, grid, geom, title, plot_options)


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

    # scale and clamp the variable
    geom[data_norm] = __scale_range_vector(geom[data_norm], scale, lim)

    # create the arrows
    glyphs = geom.glyph(orient=data_vec, scale=data_norm, factor=arrow)

    # add the resulting plot to the plotter
    pl.add_mesh(
        glyphs,
        log_scale=log,
        scalar_bar_args=scalar_bar_args,
    )

    # add the plot background (wireframe, axis, and title)
    __get_plot_base(pl, grid, geom, title, plot_options)
