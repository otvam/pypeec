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
from PyPEEC.lib_shared import plot_geometry


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
    thr = max(nrm)*arrow_threshold
    idx = nrm > thr

    # filter out the arrows that are too small
    geom = geom.extract_cells(idx)

    return geom


def _get_filter_scalar(geom, var, filter_lim):
    """
    Filter the voxel structure with provided variable limits.
    """

    # if the voxel structure is empty, nothing to do
    if geom.n_cells == 0:
        return geom

    # handle None
    (f_min, f_max) = filter_lim
    if f_min is None:
        f_min = -float("inf")
    if f_max is None:
        f_max = +float("inf")

    # get var
    data = geom[var]

    # find the filter
    idx = np.logical_and(data >= f_min, data <= f_max)

    # filter data
    geom = geom.extract_cells(idx)

    return geom


def _get_clamp_scale_scalar(geom, var, color_lim, scale):
    """
    Clamp the variable between a lower and upper bound.
    Afterwards, scale a variable.
    """

    # if the voxel structure is empty, nothing to do
    if geom.n_cells == 0:
        return geom

    # handle None
    (c_min, c_max) = color_lim
    if c_min is None:
        c_min = -float("inf")
    if c_max is None:
        c_max = +float("inf")

    # get var
    data = geom[var]

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
    cmap = ["darkorange", "forestgreen", "royalblue"]

    # add the resulting plot to the plotter
    pl.add_mesh(
        geom,
        scalars="material",
        scalar_bar_args=scalar_bar_args,
        annotations=annotations,
        cmap=cmap,
    )

    # add the plot background (wireframe, axis, and title)
    plot_geometry.get_plot_geometry(pl, grid, geom, plot_title, plot_options)


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
    geom_var = _get_filter_scalar(geom_var, var, filter_lim)
    geom_var = _get_clamp_scale_scalar(geom_var, var, color_lim, scale)

    # add the resulting plot to the plotter
    if geom_var.n_cells > 0:
        pl.add_mesh(
            geom_var,
            scalars=var,
            log_scale=log,
            scalar_bar_args=scalar_bar_args,
        )

    # add the plot background (wireframe, axis, and title)
    plot_geometry.get_plot_geometry(pl, grid, geom, plot_title, plot_options)


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
    geom_var = _get_filter_scalar(geom_var, var, filter_lim)
    geom_var = _get_clamp_scale_scalar(geom_var, var, color_lim, scale)

    # get arrow size
    factor = min(grid.spacing)*arrow_scale

    # add the resulting plot to the plotter
    if geom_var.n_cells > 0:
        pl.add_mesh(
            geom_var.glyph(orient=vec, scale=False, factor=factor),
            scalars=var,
            log_scale=log,
            scalar_bar_args=scalar_bar_args,
        )

    # add the plot background (wireframe, axis, and title)
    plot_geometry.get_plot_geometry(pl, grid, geom, plot_title, plot_options)
