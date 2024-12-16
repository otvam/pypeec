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
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import numpy as np
import numpy.linalg as lna


def _get_plot_view_theme(pl, grid, voxel, point, plot_view, plot_theme):
    """
    Plot the geometry as wireframe (complete grid and non-empty voxels).
    Plot the point cloud used for the field evaluation.
    Add the axis descriptor to orientate the geometry.
    Set the plot theme.
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
            line_width=plot_view["grid_thickness"],
        )

    # plot the non-empty voxels
    if plot_view["geom_plot"] and (voxel.n_cells > 0):
        pl.add_mesh(
            voxel,
            style="wireframe",
            color=plot_view["geom_color"],
            opacity=plot_view["geom_opacity"],
            line_width=plot_view["geom_thickness"],
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
    if plot_theme["axis_add"]:
        pl.add_axes(
            line_width=plot_theme["axis_size"],
            color=plot_theme["text_color"],
            interactive=False,
        )


def _get_plot_title(pl, title, plot_theme):
    """
    Add a title located at the corner of the plot.
    """

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


def _get_scale_norm(obj, scale):
    """
    Scale a variable between a lower and upper bound.
    The operation is done with respect to the norm variable.
    """

    # if the voxel structure is empty, nothing to do
    if obj.n_cells == 0:
        return obj

    # get var
    data = obj["norm"]

    # add scaling
    data = scale * data

    # assign data
    obj["norm"] = data

    return obj


def _get_filter_arrow(obj, arrow_threshold):
    """
    Filter the voxel structure with a variable.
    This function is used to remove arrows with extremely low lengths.
    The operation is done with respect to the norm variable.
    """

    # if the voxel structure is empty, nothing to do
    if obj.n_cells == 0:
        return obj

    # get var
    data = obj["norm"]

    # threshold for arrow removal
    if np.any(np.isfinite(data)):
        thr = np.nanmax(data) * arrow_threshold
    else:
        thr = np.nan

    # indices to be kept
    idx = data > thr

    # filter out the arrows that are too small
    obj = obj.extract_cells(idx)

    return obj


def _get_filter_norm(obj, filter_lim):
    """
    Filter the voxel structure with provided limits.
    The operation is done with respect to the norm variable.
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
    data = obj["norm"]

    # indices to be kept
    idx = np.logical_and(data >= f_min, data <= f_max)

    # filter data
    obj = obj.extract_cells(idx)

    return obj


def _get_clamp_norm(obj, clamp_lim):
    """
    Clamp a variable between a lower and upper bound.
    The operation is done with respect to the norm variable.
    """

    # if the voxel structure is empty, nothing to do
    if obj.n_cells == 0:
        return obj

    # handle None
    if clamp_lim is None:
        c_min = -float("inf")
        c_max = +float("inf")
    else:
        (c_min, c_max) = clamp_lim

    # get var
    data = obj["norm"]

    # clamp range
    data = np.maximum(data, c_min)
    data = np.minimum(data, c_max)

    # assign data
    obj["norm"] = data

    return obj


def _get_norm(obj, data_plot):
    """
    Get and prepare a scalar norm variable.
    """

    # extract
    var = data_plot["var"]
    scale = data_plot["scale"]
    filter_lim = data_plot["filter_lim"]
    clamp_lim = data_plot["clamp_lim"]

    # check variable
    if var + "_norm" not in obj.array_names:
        raise RuntimeError("variable is not in the dataset: %s" % var)

    # copy
    obj_tmp = obj.copy(deep=True)
    norm = obj_tmp[var + "_norm"]

    # scale and clamp the variable
    obj_tmp["norm"] = norm
    obj_tmp = _get_scale_norm(obj_tmp, scale)
    obj_tmp = _get_filter_norm(obj_tmp, filter_lim)
    obj_tmp = _get_clamp_norm(obj_tmp, clamp_lim)

    return obj_tmp


def _get_phasor(obj, data_plot):
    """
    Get and prepare a scalar phasor variable.
    """

    # extract
    var = data_plot["var"]
    phase = data_plot["phase"]
    scale = data_plot["scale"]
    filter_lim = data_plot["filter_lim"]
    clamp_lim = data_plot["clamp_lim"]

    # check variable
    if var + "_re" not in obj.array_names:
        raise RuntimeError("variable is not in the dataset: %s" % var)
    if var + "_im" not in obj.array_names:
        raise RuntimeError("variable is not in the dataset: %s" % var)

    # copy
    obj_tmp = obj.copy(deep=True)
    re = obj_tmp[var + "_re"]
    im = obj_tmp[var + "_im"]
    norm = np.real((re + 1j * im) * np.exp(1j * phase))

    # scale and clamp the variable
    obj_tmp["norm"] = norm
    obj_tmp = _get_scale_norm(obj_tmp, scale)
    obj_tmp = _get_filter_norm(obj_tmp, filter_lim)
    obj_tmp = _get_clamp_norm(obj_tmp, clamp_lim)

    return obj_tmp


def _get_arrow(obj, data_plot):
    """
    Get and prepare a vector phasor variable.
    """

    # extract
    var = data_plot["var"]
    phase = data_plot["phase"]
    scale = data_plot["scale"]
    filter_lim = data_plot["filter_lim"]
    clamp_lim = data_plot["clamp_lim"]
    arrow_threshold = data_plot["arrow_threshold"]

    # check variable
    if var + "_re" not in obj.array_names:
        raise RuntimeError("variable is not in the dataset: %s" % var)
    if var + "_im" not in obj.array_names:
        raise RuntimeError("variable is not in the dataset: %s" % var)

    # copy
    obj_tmp = obj.copy(deep=True)
    re = obj_tmp[var + "_re"]
    im = obj_tmp[var + "_im"]
    vector = np.real((re + 1j * im) * np.exp(1j * phase))
    norm = lna.norm(vector, axis=1)

    # scale and clamp the variable
    obj_tmp["norm"] = norm
    obj_tmp["vector"] = vector
    obj_tmp = _get_scale_norm(obj_tmp, scale)
    obj_tmp = _get_filter_norm(obj_tmp, filter_lim)
    obj_tmp = _get_filter_arrow(obj_tmp, arrow_threshold)
    obj_tmp = _get_clamp_norm(obj_tmp, clamp_lim)

    return obj_tmp


def _plot_scalar(pl, obj, data_plot, plot_clip, plot_theme):
    """
    Plot a scalar variable.
    The plot is either made on:
        - the unstructured grid describing the non-empty voxels
        - the polydata (point cloud) used to evaluate the field
    """

    # extract
    log = data_plot["log"]
    color_lim = data_plot["color_lim"]
    point_size = data_plot["point_size"]
    legend = data_plot["legend"]
    title = data_plot["title"]

    # extract
    colorbar_plot = plot_theme["colorbar_plot"]
    colorbar_size = plot_theme["colorbar_size"]
    colorbar_font = plot_theme["colorbar_font"]
    text_color = plot_theme["text_color"]

    # set title
    _get_plot_title(pl, title, plot_theme)

    # color bar options
    scalar_bar_args = dict(
        title=legend,
        n_labels=colorbar_size,
        label_font_size=colorbar_font,
        title_font_size=colorbar_font,
        color=text_color,
    )

    # add the resulting plot to the plotter
    arg = dict(
        scalars="norm",
        log_scale=log,
        clim=color_lim,
        point_size=point_size,
        show_scalar_bar=colorbar_plot,
        scalar_bar_args=scalar_bar_args,
        render_points_as_spheres=True,
    )
    if obj.n_cells > 0:
        _get_clip_mesh(pl, obj, arg, plot_clip)


def _plot_arrow(pl, grid, obj, data_plot, plot_clip, plot_theme):
    """
    Plot a vector variable with an arrow plot (quiver plot).
    The plot is either made on:
        - the unstructured grid describing the non-empty voxels
        - the polydata (point cloud) used to evaluate the field

    A scalar variable is used to determine the color of the arrows.
    The length of the arrows is constant (and scaled with respect to the voxel size).
    """

    # extract
    log = data_plot["log"]
    color_lim = data_plot["color_lim"]
    arrow_scale = data_plot["arrow_scale"]
    legend = data_plot["legend"]
    title = data_plot["title"]

    # extract
    colorbar_plot = plot_theme["colorbar_plot"]
    colorbar_size = plot_theme["colorbar_size"]
    colorbar_font = plot_theme["colorbar_font"]
    text_color = plot_theme["text_color"]

    # set title
    _get_plot_title(pl, title, plot_theme)

    # color bar options
    scalar_bar_args = dict(
        title=legend,
        n_labels=colorbar_size,
        label_font_size=colorbar_font,
        title_font_size=colorbar_font,
        color=text_color,
    )

    # get arrow size
    d_char = min(grid.spacing)
    factor = d_char * arrow_scale

    # add the resulting plot to the plotter
    arg = dict(
        scalars="norm",
        log_scale=log,
        clim=color_lim,
        show_scalar_bar=colorbar_plot,
        scalar_bar_args=scalar_bar_args,
    )
    if obj.n_cells > 0:
        glyph_tmp = obj.glyph(orient="vector", scale=False, factor=factor)
        _get_clip_mesh(pl, glyph_tmp, arg, plot_clip)


def _plot_material(pl, voxel, data_plot, plot_clip, plot_theme):
    """
    Plot the material and source description.
    """

    # extract
    color_electric = data_plot["color_electric"]
    color_magnetic = data_plot["color_magnetic"]
    color_electromagnetic = data_plot["color_electromagnetic"]
    color_current_source = data_plot["color_current_source"]
    color_voltage_source = data_plot["color_voltage_source"]
    title = data_plot["title"]

    # set title
    _get_plot_title(pl, title, plot_theme)

    # get a colormap with three discrete color
    cmap = [
        color_electric,
        color_magnetic,
        color_electromagnetic,
        color_current_source,
        color_voltage_source,
    ]

    # make a copy (for avoid cross coupling)
    voxel_tmp = voxel.copy(deep=True)

    # add the resulting plot to the plotter
    arg = dict(
        clim=[1, 5],
        show_scalar_bar=False,
        scalars="material",
        cmap=cmap,
    )
    if voxel_tmp.n_cells > 0:
        _get_clip_mesh(pl, voxel_tmp, arg, plot_clip)


def _plot_geometry(pl, voxel, data_plot, plot_clip, plot_theme, var):
    """
    Plot an integer variable on the voxel structure (material or connection).
    """

    # extract
    colormap = data_plot["colormap"]
    opacity = data_plot["opacity"]
    title = data_plot["title"]

    # set title
    _get_plot_title(pl, title, plot_theme)

    # make a copy (for avoid cross coupling)
    voxel_tmp = voxel.copy(deep=True)

    # add the resulting plot to the plotter
    arg = dict(
        show_scalar_bar=False,
        scalars=var,
        cmap=colormap,
        opacity=opacity,
    )
    if voxel_tmp.n_cells > 0:
        _get_clip_mesh(pl, voxel_tmp, arg, plot_clip)


def _plot_mesh(pl, voxel, reference, data_plot, plot_clip, plot_theme):
    """
    Plot the reference and voxelized structures in order to assess the voxelization error.
    """

    # extract the data
    color_voxel = data_plot["color_voxel"]
    color_reference = data_plot["color_reference"]
    opacity_voxel = data_plot["opacity_voxel"]
    opacity_reference = data_plot["opacity_reference"]
    title = data_plot["title"]

    # set title
    _get_plot_title(pl, title, plot_theme)

    # make a copy (for avoid cross coupling)
    voxel_tmp = voxel.copy(deep=True)
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


def get_plot_viewer(pl, grid, voxel, point, reference, layout, data_plot, data_options):
    """
    Plot the voxel structure (for the viewer).
    The following plot types are available:
        - the domains are shown for the non-empty voxels
        - the connected components for the non-empty voxels
        - the meshing tolerance between the reference and voxelized structures
    """

    # get options
    plot_clip = data_options["plot_clip"]
    plot_view = data_options["plot_view"]
    plot_theme = data_options["plot_theme"]

    # get the main plot
    if layout == "domain":
        _plot_geometry(pl, voxel, data_plot, plot_clip, plot_theme, "domain")
    elif layout == "graph":
        _plot_geometry(pl, voxel, data_plot, plot_clip, plot_theme, "graph")
    elif layout == "mesh":
        _plot_mesh(pl, voxel, reference, data_plot, plot_clip, plot_theme)
    else:
        raise ValueError("invalid plot type and plot feature")

    # add the wireframe and axis
    _get_plot_view_theme(pl, grid, voxel, point, plot_view, plot_theme)


def get_plot_plotter(pl, grid, voxel, point, layout, data_plot, data_options):
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
    plot_clip = data_options["plot_clip"]
    plot_view = data_options["plot_view"]
    plot_theme = data_options["plot_theme"]

    # get the plot dataset
    if layout == "material":
        obj = voxel
    elif layout in ["norm_voxel", "phasor_voxel", "arrow_voxel"]:
        obj = voxel
    elif layout in ["norm_point", "phasor_point", "arrow_point"]:
        obj = point
    else:
        raise ValueError("invalid plot type and plot feature")

    # plot the geometry
    if layout == "material":
        _plot_material(pl, voxel, data_plot, plot_clip, plot_theme)
    elif layout in ["norm_voxel", "norm_point"]:
        obj = _get_norm(obj, data_plot)
        _plot_scalar(pl, obj, data_plot, plot_clip, plot_theme)
    elif layout in ["phasor_voxel", "phasor_point"]:
        obj = _get_phasor(obj, data_plot)
        _plot_scalar(pl, obj, data_plot, plot_clip, plot_theme)
    elif layout in ["arrow_voxel", "arrow_point"]:
        obj = _get_arrow(obj, data_plot)
        _plot_arrow(pl, grid, obj, data_plot, plot_clip, plot_theme)
    else:
        raise ValueError("invalid plot type and plot feature")

    # add the wireframe and axis
    _get_plot_view_theme(pl, grid, voxel, point, plot_view, plot_theme)
