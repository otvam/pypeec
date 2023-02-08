"""
Different functions for plotting voxel structures with PyVista.

For the viewer and the plotter, the following object are shown:
    - the complete voxel structure (as wireframe)
    - the structure containing non-empty voxels (as wireframe)
    - the defined point cloud (as points)

For the viewer, the following plots are available:
    - the domains are shown for the non-empty voxels
    - the connected components for the non-empty voxels

For the plotter, the following plots are available:
    - material description for the non-empty voxels (conductors and sources)
    - scalar plots for the non-empty voxels
    - arrow plots for the non-empty voxels
    - scalar plots for the point cloud
    - arrow plots for the point cloud
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np
import numpy.linalg as lna


def _get_plot_options(pl, grid, voxel, point, plot_options):
    """
    Plot the geometry as wireframe (complete grid and non-empty voxels).
    Plot the point cloud used for the field evaluation.
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
    pl.add_axes(line_width=2, interactive=False)
    pl.add_text(plot_options["title"], font_size=10)


def _get_clip_mesh(pl, obj, arg, clip_options):
    """
    Add an object (either full view or clipped).
    """

    # extract
    clip_plot = clip_options["clip_plot"]
    clip_invert = clip_options["clip_invert"]
    clip_axis = clip_options["clip_axis"]
    clip_value = clip_options["clip_value"]

    # add the plot
    if clip_plot:
        # add the clipping arguments
        arg["invert"] = clip_invert
        arg["normal"] = clip_axis
        arg["value"] = clip_value
        arg["normal_rotation"] = False

        # add the clipped plot
        pl.add_mesh_clip_plane(
            obj,
            **arg,
        )
    else:
        # add the full plot
        pl.add_mesh(
            obj,
            **arg,
        )


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
    thr = np.nanmax(nrm)*arrow_threshold
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


def plot_material(pl, voxel, data_options, clip_options):
    """
    Plot the material description (conductors, voltage sources, and current sources).
    The plot is made on the unstructured grid describing the non-empty voxels.
    The following fake scalar field encoding is used:
        - 0: conducting voxels
        - 1: current source voxels
        - 2: voltage source voxels
    """

    # get a colormap with three discrete color
    cmap = ["darkorange", "gainsboro", "forestgreen", "royalblue"]

    # make a copy (for avoid cross coupling)
    voxel_tmp = voxel.copy(deep=True)

    # add the resulting plot to the plotter
    arg = dict(
        clim=[1, 4],
        show_scalar_bar=False,
        scalars="material",
        cmap=cmap,
    )
    if voxel_tmp.n_cells > 0:
        _get_clip_mesh(pl, voxel_tmp, arg, clip_options)


def plot_scalar(pl, obj, data_options, clip_options):
    """
    Plot a scalar variable (resistivity, potential, current density, or magnetic field).
    The plot is either made on:
        - the unstructured grid describing the non-empty voxels
        - the polydata (point cloud) used to evaluate the field
    """

    # extract
    var = data_options["var"]
    scale = data_options["scale"]
    log = data_options["log"]
    filter_lim = data_options["filter_lim"]
    color_lim = data_options["color_lim"]
    point_size = data_options["point_size"]
    legend = data_options["legend"]

    # color bar options
    scalar_bar_args = dict(
        n_labels=5,
        label_font_size=15,
        title_font_size=15,
        title=legend,
    )

    # scale and clamp the variable
    obj_tmp = obj.copy(deep=True)
    obj_tmp = _get_filter_scalar(obj_tmp, var, filter_lim)
    obj_tmp = _get_clamp_scale_scalar(obj_tmp, var, color_lim, scale)

    # add the resulting plot to the plotter
    arg = dict(
        scalars=var,
        log_scale=log,
        point_size=point_size,
        scalar_bar_args=scalar_bar_args,
        render_points_as_spheres=True,
    )
    if obj_tmp.n_cells > 0:
        _get_clip_mesh(pl, obj_tmp, arg, clip_options)


def plot_arrow(pl, d_char, obj, data_options, clip_options):
    """
    Plot a vector variable (current density or magnetic field) with an arrow plot (quiver plot).
    The plot is either made on:
        - the unstructured grid describing the non-empty voxels
        - the polydata (point cloud) used to evaluate the field

    A scalar variable is used to determine the color of the arrows.
    The length of the arrows is constant (and scaled with respect to the voxel size).
    """

    # extract
    var_scalar = data_options["var_scalar"]
    var_vector = data_options["var_vector"]
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
    obj_tmp = obj.copy(deep=True)
    obj_tmp = _get_filter_vector(obj_tmp, var_vector, arrow_threshold)
    obj_tmp = _get_filter_scalar(obj_tmp, var_scalar, filter_lim)
    obj_tmp = _get_clamp_scale_scalar(obj_tmp, var_scalar, color_lim, scale)

    # get arrow size
    factor = d_char*arrow_scale

    # add the resulting plot to the plotter
    arg = dict(scalars=var_scalar, log_scale=log, scalar_bar_args=scalar_bar_args)
    if obj_tmp.n_cells > 0:
        glyph_tmp = obj_tmp.glyph(orient=var_vector, scale=False, factor=factor)
        _get_clip_mesh(pl, glyph_tmp, arg, clip_options)


def get_plot_viewer(pl, grid, voxel, point, data_plot):
    """
    Plot the voxel structure (for the viewer).
    The following plot types are available:
        - the domains are shown for the non-empty voxels
        - the connected components for the non-empty voxels
    """

    # get the data
    plot_type = data_plot["plot_type"]
    clip_options = data_plot["clip_options"]
    plot_options = data_plot["plot_options"]

    # find the variable to be plotted
    if plot_type == "domain":
        tag = "domain"
    elif plot_type == "connection":
        tag = "connection"
    else:
        raise ValueError("invalid plot type and plot feature")

    # make a copy (for avoid cross coupling)
    voxel_tmp = voxel.copy(deep=True)

    # add the resulting plot to the plotter
    arg = dict(
        show_scalar_bar=False,
        scalars=tag,
        cmap="Accent",
    )
    if voxel_tmp.n_cells > 0:
        _get_clip_mesh(pl, voxel_tmp, arg, clip_options)

    # add the wireframe and axis
    _get_plot_options(pl, grid, voxel, point, plot_options)


def get_plot_plotter(pl, grid, voxel, point, data_plot):
    """
    Plot the solution (for the plotter).
    The following plot types are available:
        - plot the material description (conductors and sources) on the voxel structure
        - plot a scalar variable on the voxel structure
        - plot a scalar variable on the point cloud
        - plot a vector variable on the voxel structure
        - plot a vector variable on the point cloud
    """

    # get the data
    plot_type = data_plot["plot_type"]
    data_options = data_plot["data_options"]
    clip_options = data_plot["clip_options"]
    plot_options = data_plot["plot_options"]

    # get the main plot
    if plot_type == "material":
        plot_material(pl, voxel, data_options, clip_options)
    elif plot_type == "scalar_voxel":
        plot_scalar(pl, voxel, data_options, clip_options)
    elif plot_type == "scalar_point":
        plot_scalar(pl, point, data_options, clip_options)
    elif plot_type == "arrow_voxel":
        d_char = min(grid.spacing)
        plot_arrow(pl, d_char, voxel, data_options, clip_options)
    elif plot_type == "arrow_point":
        d_char = min(grid.spacing)
        plot_arrow(pl, d_char, point, data_options, clip_options)
    else:
        raise ValueError("invalid plot type and plot feature")

    # add the wireframe and axis
    _get_plot_options(pl, grid, voxel, point, plot_options)
