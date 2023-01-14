"""
Different functions for plotting a voxel structure.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

from PyPEEC.lib_shared import plot_geometry


def get_plot_viewer(pl, grid, geom, plot_title, plot_options):
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

    # add the plot background (wireframe, axis, and title)
    plot_geometry.get_plot_geometry(pl, grid, geom, plot_title, plot_options)

