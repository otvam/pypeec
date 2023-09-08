"""
User script for visualizing a 3D voxel structure.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import sys
import os.path
from pypeec import main
import examples_config

# get config
PATH_ROOT = examples_config.PATH_ROOT
FOLDER_CONFIG = examples_config.FOLDER_CONFIG
FOLDER_NAME = examples_config.FOLDER_NAME
EXAMPLE_NAME = examples_config.EXAMPLE_NAME


if __name__ == "__main__":
    # get the filenames
    file_voxel = os.path.join(PATH_ROOT, FOLDER_NAME, EXAMPLE_NAME, "voxel.pck")
    file_point = os.path.join(PATH_ROOT, FOLDER_NAME, EXAMPLE_NAME, "point.yaml")
    file_viewer = os.path.join(PATH_ROOT, FOLDER_CONFIG, "viewer.yaml")

    # plot type
    tag_plot = ["domain", "connection"]

    # run viewer
    (status, ex) = main.run_viewer_file(
        file_voxel, file_point, file_viewer,
        tag_plot=tag_plot,
        plot_mode="qt",
    )
    sys.exit(int(not status))
