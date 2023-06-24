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
    - material description for the non-empty voxels
    - scalar plots for the non-empty voxels
    - arrow plots for the non-empty voxels
    - scalar plots for the point cloud
    - arrow plots for the point cloud
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import numpy as np
import numpy.linalg as lna


def _get_plot_view(pl, title, grid, voxel, point, plot_view, plot_theme):
    """
    Plot the geometry as wireframe (complete grid and non-empty voxels).
    Plot the point cloud used for the field evaluation.
    Add the axis descriptor to orientate the geometry.
    Add a plot title.
    """

    # set background
    pl.set_background(plot_theme["background_color"])

    # plot the complete grid
    if plot_view["grid_plot"] and (grid.n_cells > 0):
        pl.add_mesh(
            grid,
            style="wireframe",
            color=plot_view["grid_color"],
            opacity=plot_view["grid_opacity"],
            line_width=plot_view["grid_thickness"]
        )

    # plot the non-empty voxels
    if plot_view["geom_plot"] and (voxel.n_cells > 0):
        pl.add_mesh(
            voxel,
            style="wireframe",
            color=plot_view["geom_color"],
            opacity=plot_view["geom_opacity"],
            line_width=plot_view["geom_thickness"]
        )

    # plot the cloud points
    if plot_view["point_plot"] and (point.n_cells > 0):
        pl.add_mesh(
            point,
            color=plot_view["point_color"],
            point_size=plot_view["point_size"],
            opacity=plot_view["point_opacity"],
            render_points_as_spheres=True,
        )

    # set the camera position
    if plot_view["camera_roll"] is not None:
        pl.camera.roll = plot_view["camera_roll"]
    if plot_view["camera_azimuth"] is not None:
        pl.camera.azimuth = plot_view["camera_azimuth"]
    if plot_view["camera_elevation"] is not None:
        pl.camera.elevation = plot_view["camera_elevation"]

    # add axes
    pl.add_axes(
        line_width=plot_theme["axis_size"],
        color=plot_theme["text_color"],
        interactive=False,
    )

    # add titles
    pl.add_text(
        title,
        font_size=plot_theme["title_font"],
        color=plot_theme["text_color"],
    )


def _get_clip_mesh(pl, obj, arg, plot_clip):
    """
    Add an object (either full view or clipped).
    """

    # extract
    clip_plot = plot_clip["clip_plot"]
    clip_invert = plot_clip["clip_invert"]
    clip_axis = plot_clip["clip_axis"]
    clip_value = plot_clip["clip_value"]

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
    if np.any(np.isfinite(nrm)):
        thr = np.nanmax(nrm)*arrow_threshold
    else:
        thr = np.nan

    # indices to be kept
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
    if filter_lim is None:
        f_min = -float("inf")
        f_max = +float("inf")
    else:
        (f_min, f_max) = filter_lim

    # get var
    data = obj[var]

    # indices to be kept
    idx = np.logical_and(data >= f_min, data <= f_max)

    # filter data
    obj = obj.extract_cells(idx)

    return obj


def _get_clamp_scale_scalar(obj, var, color_lim, scale):
    """
    Clamp a scalar variable between a lower and upper bound.
    Afterward, the clamped variable is scaled.
    """

    # if the voxel structure is empty, nothing to do
    if obj.n_cells == 0:
        return obj

    # handle None
    if color_lim is None:
        c_min = -float("inf")
        c_max = +float("inf")
    else:
        (c_min, c_max) = color_lim

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


def _plot_scalar(pl, obj, plot_content, plot_clip, plot_theme):
    """
    Plot a scalar variable.
    The plot is either made on:
        - the unstructured grid describing the non-empty voxels
        - the polydata (point cloud) used to evaluate the field
    """

    # extract
    var = plot_content["var"]
    scale = plot_content["scale"]
    log = plot_content["log"]
    filter_lim = plot_content["filter_lim"]
    color_lim = plot_content["color_lim"]
    point_size = plot_content["point_size"]
    legend = plot_content["legend"]

    # color bar options
    scalar_bar_args = dict(
        title=legend,
        n_labels=plot_theme["colorbar_size"],
        label_font_size=plot_theme["colorbar_font"],
        title_font_size=plot_theme["colorbar_font"],
        color=plot_theme["text_color"],
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
        _get_clip_mesh(pl, obj_tmp, arg, plot_clip)


def _plot_arrow(pl, grid, obj, plot_content, plot_clip, plot_theme):
    """
    Plot a vector variable with an arrow plot (quiver plot).
    The plot is either made on:
        - the unstructured grid describing the non-empty voxels
        - the polydata (point cloud) used to evaluate the field

    A scalar variable is used to determine the color of the arrows.
    The length of the arrows is constant (and scaled with respect to the voxel size).
    """

    # extract
    var_scalar = plot_content["var_scalar"]
    var_vector = plot_content["var_vector"]
    scale = plot_content["scale"]
    log = plot_content["log"]
    filter_lim = plot_content["filter_lim"]
    color_lim = plot_content["color_lim"]
    arrow_scale = plot_content["arrow_scale"]
    arrow_threshold = plot_content["arrow_threshold"]
    legend = plot_content["legend"]

    # color bar options
    scalar_bar_args = dict(
        title=legend,
        n_labels=plot_theme["colorbar_size"],
        label_font_size=plot_theme["colorbar_font"],
        title_font_size=plot_theme["colorbar_font"],
        color=plot_theme["text_color"],
    )

    # scale and clamp the variable
    obj_tmp = obj.copy(deep=True)
    obj_tmp = _get_filter_vector(obj_tmp, var_vector, arrow_threshold)
    obj_tmp = _get_filter_scalar(obj_tmp, var_scalar, filter_lim)
    obj_tmp = _get_clamp_scale_scalar(obj_tmp, var_scalar, color_lim, scale)

    # get arrow size
    d_char = min(grid.spacing)
    factor = d_char*arrow_scale

    # add the resulting plot to the plotter
    arg = dict(scalars=var_scalar, log_scale=log, scalar_bar_args=scalar_bar_args)
    if obj_tmp.n_cells > 0:
        glyph_tmp = obj_tmp.glyph(orient=var_vector, scale=False, factor=factor)
        _get_clip_mesh(pl, glyph_tmp, arg, plot_clip)


def _plot_material(pl, voxel, plot_content, plot_clip):
    """
    Plot the material and source description.
    """

    # get a colormap with three discrete color
    cmap = [
        plot_content["color_electric"],
        plot_content["color_magnetic"],
        plot_content["color_current_source"],
        plot_content["color_voltage_source"],
    ]

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
        _get_clip_mesh(pl, voxel_tmp, arg, plot_clip)


def _plot_geometry(pl, voxel, plot_content, plot_clip, tag):
    """
    Plot an integer variable on the voxel structure (material or connection).
    """

    # extract
    colormap = plot_content["colormap"]
    opacity = plot_content["opacity"]

    # make a copy (for avoid cross coupling)
    voxel_tmp = voxel.copy(deep=True)

    # add the resulting plot to the plotter
    arg = dict(
        show_scalar_bar=False,
        scalars=tag,
        cmap=colormap,
        opacity=opacity,
    )
    if voxel_tmp.n_cells > 0:
        _get_clip_mesh(pl, voxel_tmp, arg, plot_clip)


def _plot_voxelization(pl, voxel, reference, plot_content, plot_clip):
    """
    Plot the reference and voxelized structures in order to assess the voxelization error.
    """

    # extract the data
    color_voxel = plot_content["color_voxel"]
    color_reference = plot_content["color_reference"]
    opacity_voxel = plot_content["opacity_voxel"]
    opacity_reference = plot_content["opacity_reference"]
    
    # make a copy (for avoid cross coupling)
    voxel_tmp = voxel.copy(deep=True)

    # if the reference is not provided, use the voxel structure
    if reference is None:
        reference_tmp = voxel.copy(deep=True)
    else:
        reference_tmp = reference.copy(deep=True)

    # add the resulting plot to the plotter
    arg = dict(
        show_scalar_bar=False,
        color=color_voxel,
        opacity=opacity_voxel,
    )
    if voxel_tmp.n_cells > 0:
        _get_clip_mesh(pl, voxel_tmp, arg, plot_clip)

    # add the resulting plot to the plotter
    arg = dict(
        show_scalar_bar=False,
        color=color_reference,
        opacity=opacity_reference,
    )
    if voxel_tmp.n_cells > 0:
        _get_clip_mesh(pl, reference_tmp, arg, plot_clip)


def get_plot_viewer(pl, title, grid, voxel, point, reference, data_plot, data_options):
    """
    Plot the voxel structure (for the viewer).
    The following plot types are available:
        - the domains are shown for the non-empty voxels
        - the connected components for the non-empty voxels
        - the meshing tolerance between the reference and voxelized structures
    """

    # extract the data
    plot_type = data_plot["plot_type"]
    plot_content = data_plot["plot_content"]
    plot_clip = data_options["plot_clip"]
    plot_view = data_options["plot_view"]
    plot_theme = data_options["plot_theme"]

    # get the main plot
    if plot_type == "domain":
        _plot_geometry(pl, voxel, plot_content, plot_clip, "domain")
    elif plot_type == "connection":
        _plot_geometry(pl, voxel, plot_content, plot_clip, "connection")
    elif plot_type == "voxelization":
        _plot_voxelization(pl, voxel, reference, plot_content, plot_clip)
    else:
        raise ValueError("invalid plot type and plot feature")

    # add the wireframe and axis
    _get_plot_view(pl, title, grid, voxel, point, plot_view, plot_theme)


def get_plot_plotter(pl, title, grid, voxel, point, data_plot):
    """
    Plot the solution (for the plotter).
    The following plot types are available:
        - plot the material and source description on the voxel structure
        - plot a scalar variable on the voxel structure
        - plot a scalar variable on the point cloud
        - plot a vector variable on the voxel structure
        - plot a vector variable on the point cloud
    """

    # extract the data
    plot_type = data_plot["plot_type"]
    plot_content = data_plot["plot_content"]
    plot_clip = data_plot["plot_clip"]
    plot_view = data_plot["plot_view"]
    plot_theme = data_plot["plot_theme"]

    # get the main plot
    if plot_type == "material":
        _plot_material(pl, voxel, plot_content, plot_clip)
    elif plot_type == "scalar_voxel":
        _plot_scalar(pl, voxel, plot_content, plot_clip, plot_theme)
    elif plot_type == "scalar_point":
        _plot_scalar(pl, point, plot_content, plot_clip, plot_theme)
    elif plot_type == "arrow_voxel":
        _plot_arrow(pl, grid, voxel, plot_content, plot_clip, plot_theme)
    elif plot_type == "arrow_point":
        _plot_arrow(pl, grid, point, plot_content, plot_clip, plot_theme)
    else:
        raise ValueError("invalid plot type and plot feature")

    # add the wireframe and axis
    _get_plot_view(pl, title, grid, voxel, point, plot_view, plot_theme)
