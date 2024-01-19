"""
Script for plotting the geometry of the examples.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import os.path
from pypeec import main
from pypeec import io

# get the path of the root of the code
PATH_ROOT = os.path.dirname(__file__)


def run_image(folder_example):
    """
    Run the mesher for a specified example.
    Plot the geometry with an empty background.
    """

    # example folder
    folder_base = os.path.join(PATH_ROOT, "..", "..", "examples")

    # get the geometry file
    file_geometry = os.path.join(folder_base, folder_example, "geometry.yaml")

    # get the viewer file
    file_viewer = os.path.join(folder_base, "config", "viewer.yaml")

    # load data
    data_geometry = io.load_config(file_geometry)
    data_viewer = io.load_config(file_viewer)

    # tweak the plot options
    data_viewer["domain"]["data_window"]["show_menu"] = True
    data_viewer["domain"]["data_window"]["window_size"] = [400, 300]
    data_viewer["domain"]["data_options"]["plot_theme"]["background_color"] = "white"
    data_viewer["domain"]["data_options"]["plot_theme"]["axis_add"] = False
    data_viewer["domain"]["data_options"]["plot_view"]["grid_plot"] = False
    data_viewer["domain"]["data_options"]["plot_view"]["geom_plot"] = False
    data_viewer["domain"]["data_options"]["plot_view"]["point_plot"] = False
    data_viewer["domain"]["data_plot"]["title"] = None

    # run the mesher
    data_voxel = main.run_mesher_data(data_geometry)

    # run the viewer
    main.run_viewer_data(
        data_voxel, data_viewer,
        plot_mode="qt", tag_plot=["domain"],
    )


if __name__ == "__main__":
    run_image("tutorial")
