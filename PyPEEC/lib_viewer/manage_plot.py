"""
Different functions for plotting a voxel structure.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np
import pyvista as pv


def get_plot_base(pl, grid, geom, plot_title, plot_options):
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


def get_plot_domain(pl, geom):
    """
    Plot the different domains composing the voxel structure.
    The variable is plotted on the faces of the voxels.
    """

    # copy to avoid a mess with scaling
    geom = geom.copy(deep=True)

    # add the resulting plot to the plotter
    pl.add_mesh(
        geom,
        show_scalar_bar=False,
        scalars="domain",
        cmap="Accent",
    )
