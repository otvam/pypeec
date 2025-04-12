"""
User script for visualizing a 3D voxel structure.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import os.path
import pypeec
import examples_config

# get the path of the root of the code
PATH_ROOT = os.path.dirname(__file__)

# get config
FOLDER_CONFIG = examples_config.FOLDER_CONFIG
FOLDER_EXAMPLE = examples_config.FOLDER_EXAMPLE


if __name__ == "__main__":
    # get the filenames
    file_voxel = os.path.join(PATH_ROOT, FOLDER_EXAMPLE, "voxel.json.gz")
    file_viewer = os.path.join(PATH_ROOT, FOLDER_CONFIG, "viewer.yaml")

    # list of plots to be shown (defined in viewer.yaml)
    tag_plot = ["domain", "graph"]

    # method used for rendering the plots
    plot_mode = "qt"

    # run viewer
    pypeec.run_viewer_file(
        file_voxel=file_voxel,
        file_viewer=file_viewer,
        tag_plot=tag_plot,
        plot_mode=plot_mode,
    )
