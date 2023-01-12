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
import numpy.linalg as lna
import pyvista as pv


def _get_plot_base(pl, grid, geom, plot_title, plot_options):
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
    pl.add_text(plot_title, font_size=10)


def _get_filter_vector(geom, vec, arrow_threshold):
    """
    Filter the voxel structure with a vector field.
    This function is used to remove arrow with extremely low lengths.
    """

    # if the voxel structure is empty, nothing to do
    if geom.n_cells == 0:
        return geom

    # get var
    data = geom[vec]

    # get norm
    nrm = lna.norm(data, axis=1)

    # threshold for arrow removal
    thr = np.max(nrm)*arrow_threshold

    # filter out the arrows that are too small
    idx = nrm > thr
    geom = geom.extract_cells(idx)

    return geom


def _get_filter_scalar(geom, var, filter_lim, color_lim, scale):
    """
    Filter the voxel structure with provided variable limits.
    Clamp the variable between a lower and upper bound.
    Scale a variable.
    """

    # if the voxel structure is empty, nothing to do
    if geom.n_cells == 0:
        return geom

    # handle None
    (f_min, f_max) = filter_lim
    (c_min, c_max) = color_lim
    if f_min is None:
        f_min = -float("inf")
    if f_max is None:
        f_max = +float("inf")
    if c_min is None:
        c_min = -float("inf")
    if c_max is None:
        c_max = +float("inf")

    # filter data
    geom = geom.threshold(value=(f_min, f_max), scalars=var)

    # convert to numpy
    data = geom[var]
    data = np.array(data)

    # clamp range
    data = np.maximum(data, c_min)
    data = np.minimum(data, c_max)

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
    plot_legend = data_options["plot_legend"]
    plot_title = data_options["plot_title"]

    # color bar options (no label as the positions are indicated with annotations)
    scalar_bar_args = dict(
        n_labels=0,
        label_font_size=15,
        title_font_size=15,
        title=plot_legend,
    )

    # get annotations
    annotations = {
        0: "Conductor",
        1: "Current Src.",
        2: "Voltage Src.",
    }

    # get a colormap with three discrete color
    cmap = ["yellow", "green", "blue"]

    # add the resulting plot to the plotter
    pl.add_mesh(
        geom,
        scalars="material",
        scalar_bar_args=scalar_bar_args,
        annotations=annotations,
        cmap=cmap,
    )

    # add the plot background (wireframe, axis, and title)
    _get_plot_base(pl, grid, geom, plot_title, plot_options)


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
    plot_legend = data_options["plot_legend"]
    plot_title = data_options["plot_title"]

    # color bar options
    scalar_bar_args = dict(
        n_labels=5,
        label_font_size=15,
        title_font_size=15,
        title=plot_legend,
    )

    # scale and clamp the variable
    geom_var = geom.copy(deep=True)
    geom_var = _get_filter_scalar(geom_var, var, filter_lim, color_lim, scale)

    # add the resulting plot to the plotter
    if geom_var.n_cells > 0:
        pl.add_mesh(
            geom_var,
            scalars=var,
            log_scale=log,
            scalar_bar_args=scalar_bar_args,
        )

    # add the plot background (wireframe, axis, and title)
    _get_plot_base(pl, grid, geom, plot_title, plot_options)


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
    log = data_options["log"]
    filter_lim = data_options["filter_lim"]
    color_lim = data_options["color_lim"]
    arrow_scale = data_options["arrow_scale"]
    arrow_threshold = data_options["arrow_threshold"]

    plot_legend = data_options["plot_legend"]
    plot_title = data_options["plot_title"]

    # color bar options
    scalar_bar_args = dict(
        n_labels=5,
        label_font_size=15,
        title_font_size=15,
        title=plot_legend,
    )

    # scale and clamp the variable
    geom_var = geom.copy(deep=True)
    geom_var = _get_filter_vector(geom_var, vec, arrow_threshold)
    geom_var = _get_filter_scalar(geom_var, var, filter_lim, color_lim, scale)

    # get arrow size
    factor = np.min(grid.spacing)*arrow_scale

    # add the resulting plot to the plotter
    if geom_var.n_cells > 0:
        pl.add_mesh(
            geom_var.glyph(orient=vec, scale=False, factor=factor),
            scalars=var,
            log_scale=log,
            scalar_bar_args=scalar_bar_args,
        )

    # add the plot background (wireframe, axis, and title)
    _get_plot_base(pl, grid, geom, plot_title, plot_options)
