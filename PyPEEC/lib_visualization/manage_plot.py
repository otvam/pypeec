"""
Different functions for plotting voxel structures with PyVista.

For the viewer, the geometry and the domains are plotted.

For the plotter, the following plots are available:
    - material description (conductors, voltage sources, and current sources)
    - scalar plots (resistivity, potential, and current density)
    - arrow plots (current density)
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np
import numpy.linalg as lna


def _get_filter_vector(obj, vec, arrow_threshold):
    """
    Filter the voxel structure with a vector field.
    This function is used to remove arrows with extremely low lengths.
    """

    # if the voxel structure is empty, nothing to do
    if obj.n_cells == 0:
        return obj

    # get var
    data = obj[vec]

    # get norm
    nrm = lna.norm(data, axis=1)

    # threshold for arrow removal
    thr = max(nrm)*arrow_threshold
    idx = nrm > thr

    # filter out the arrows that are too small
    obj = obj.extract_cells(idx)

    return obj


def _get_filter_scalar(obj, var, filter_lim):
    """
    Filter the voxel structure with provided limits with respect to a scalar variable.
    """

    # if the voxel structure is empty, nothing to do
    if obj.n_cells == 0:
        return obj

    # handle None
    (f_min, f_max) = filter_lim
    if f_min is None:
        f_min = -float("inf")
    if f_max is None:
        f_max = +float("inf")

    # get var
    data = obj[var]

    # find the filter
    idx = np.logical_and(data >= f_min, data <= f_max)

    # filter data
    obj = obj.extract_cells(idx)

    return obj


def _get_clamp_scale_scalar(obj, var, color_lim, scale):
    """
    Clamp a scalar variable between a lower and upper bound.
    Afterwards, the clamped variable is scaled.
    """

    # if the voxel structure is empty, nothing to do
    if obj.n_cells == 0:
        return obj

    # handle None
    (c_min, c_max) = color_lim
    if c_min is None:
        c_min = -float("inf")
    if c_max is None:
        c_max = +float("inf")

    # get var
    data = obj[var]

    # clamp range
    data = np.maximum(data, c_min)
    data = np.minimum(data, c_max)

    # add scaling
    data = scale*data

    # assign data
    obj[var] = data

    return obj


def plot_material(pl, obj, data_options):
    """
    Plot the material description (conductors, voltage sources, and current sources).
    The following encoding is used:
        - 0: conducting voxels
        - 1: current source voxels
        - 2: voltage source voxels
    """

    # extract
    legend = data_options["legend"]
    opacity = data_options["opacity"]

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
    cmap = ["darkorange", "forestgreen", "royalblue"]

    # add the resulting plot to the plotter
    pl.add_mesh(
        obj,
        scalars="material",
        opacity=opacity,
        scalar_bar_args=scalar_bar_args,
        annotations=annotations,
        cmap=cmap,
    )


def plot_scalar(pl, obj, data_options):
    """
    Plot a scalar variable (resistivity, potential, or current density).
    The variable is plotted on the faces of the voxels.
    """

    # extract
    var = data_options["var"]
    scale = data_options["scale"]
    log = data_options["log"]
    filter_lim = data_options["filter_lim"]
    color_lim = data_options["color_lim"]
    legend = data_options["legend"]
    opacity = data_options["opacity"]
    size = data_options["size"]

    # color bar options
    scalar_bar_args = dict(
        n_labels=5,
        label_font_size=15,
        title_font_size=15,
        title=legend,
    )

    # scale and clamp the variable
    geom_var = obj.copy(deep=True)
    geom_var = _get_filter_scalar(geom_var, var, filter_lim)
    geom_var = _get_clamp_scale_scalar(geom_var, var, color_lim, scale)

    # add the resulting plot to the plotter
    if geom_var.n_cells > 0:
        pl.add_mesh(
            geom_var,
            scalars=var,
            opacity=opacity,
            point_size=size,
            log_scale=log,
            scalar_bar_args=scalar_bar_args,
            render_points_as_spheres=True,
        )


def plot_arrow(pl, d_char, obj, data_options):
    """
    Plot a vector variable (current density) with an arrow plot (quiver plot).
    A scalar variable is used to determine the color of the arrows.
    The arrows are located at the center of the voxels.
    """

    # extract
    var = data_options["var"]
    vec = data_options["vec"]
    scale = data_options["scale"]
    log = data_options["log"]
    filter_lim = data_options["filter_lim"]
    color_lim = data_options["color_lim"]
    arrow_scale = data_options["arrow_scale"]
    arrow_threshold = data_options["arrow_threshold"]
    legend = data_options["legend"]

    # color bar options
    scalar_bar_args = dict(
        n_labels=5,
        label_font_size=15,
        title_font_size=15,
        title=legend,
    )

    # scale and clamp the variable
    geom_var = obj.copy(deep=True)
    geom_var = _get_filter_vector(geom_var, vec, arrow_threshold)
    geom_var = _get_filter_scalar(geom_var, var, filter_lim)
    geom_var = _get_clamp_scale_scalar(geom_var, var, color_lim, scale)

    # get arrow size
    factor = d_char*arrow_scale

    # add the resulting plot to the plotter
    if geom_var.n_cells > 0:
        pl.add_mesh(
            geom_var.glyph(orient=vec, scale=False, factor=factor),
            scalars=var,
            log_scale=log,
            scalar_bar_args=scalar_bar_args,
        )


def get_plot_options(pl, grid, voxel, point, plot_options):
    """
    Plot the geometry as wireframe (complete grid and non-empty voxels).
    Add the axis descriptor to orientate the geometry.
    Add a plot title.
    """

    # plot the complete grid
    if plot_options["grid_plot"] and (grid.n_cells > 0):
        pl.add_mesh(
            grid,
            style="wireframe",
            color=plot_options["grid_color"],
            opacity=plot_options["grid_opacity"],
            line_width=plot_options["grid_thickness"]
        )

    # plot the non-empty voxels
    if plot_options["geom_plot"] and (voxel.n_cells > 0):
        pl.add_mesh(
            voxel,
            style="wireframe",
            color=plot_options["geom_color"],
            opacity=plot_options["geom_opacity"],
            line_width=plot_options["geom_thickness"]
        )

    if plot_options["cloud_plot"] and (point.n_cells > 0):
        pl.add_mesh(
            point,
            color=plot_options["cloud_color"],
            point_size=plot_options["cloud_size"],
            opacity=plot_options["cloud_opacity"],
            render_points_as_spheres=True,
        )

    # add title and axes
    pl.add_axes(line_width=2)
    pl.add_text(plot_options["title"], font_size=10)


def get_plot_viewer(pl, voxel):
    """
    Plot the different domains composing the voxel structure.
    The variable is plotted on the faces of the voxels.
    """

    # add the resulting plot to the plotter
    pl.add_mesh(
        voxel,
        show_scalar_bar=False,
        scalars="tag",
        cmap="Accent",
    )


def get_plot_plotter(pl, grid, voxel, point, plot_type, plot_geom, data_options):
    if (plot_type == "material") and (plot_geom == "material"):
        plot_material(pl, voxel, data_options)
    elif (plot_type == "scalar") and (plot_geom == "voxel"):
        plot_scalar(pl, voxel, data_options)
    elif (plot_type == "scalar") and (plot_geom == "point"):
        plot_scalar(pl, point, data_options)
    elif (plot_type == "arrow") and (plot_geom == "voxel"):
        d_char = min(grid.spacing)
        plot_arrow(pl, d_char, voxel, data_options)
    elif (plot_type == "arrow") and (plot_geom == "point"):
        d_char = min(grid.spacing)
        plot_arrow(pl, d_char, point, data_options)
    else:
        raise ValueError("invalid plot type and plot feature")
