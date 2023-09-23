"""
Script for plotting the geometry of the examples.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import os.path
from pypeec import main
from pypeec import io


def run_image(folder_name, example_name):
    """
    Run the mesher for a specified example.
    Plot the geometry with an empty background.
    """

    # get the filenames
    file_geometry = os.path.join("examples", folder_name, example_name, "geometry.yaml")
    file_voxel = os.path.join("examples", folder_name, example_name, "voxel.pck")
    file_viewer = os.path.join("examples", "config", "viewer.yaml")

    # run the mesher
    main.run_mesher_file(file_geometry, file_voxel)

    # load data
    data_point = []
    data_voxel = io.load_pickle(file_voxel)
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

    # run viewer
    main.run_viewer_data(
        data_voxel, data_point, data_viewer,
        plot_mode="qt", tag_plot=["domain"],
    )


if __name__ == "__main__":
    run_image("examples_shape", "coplanar")
