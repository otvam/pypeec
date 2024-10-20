"""
User script for visualizing a 3D voxel structure.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import sys
import os.path
import pypeec
import examples_config

# get config
PATH_ROOT = examples_config.PATH_ROOT
FOLDER_CONFIG = examples_config.FOLDER_CONFIG
FOLDER_EXAMPLE = examples_config.FOLDER_EXAMPLE


if __name__ == "__main__":
    # get the filenames
    file_voxel = os.path.join(PATH_ROOT, FOLDER_EXAMPLE, "voxel.json.gz")
    file_viewer = os.path.join(PATH_ROOT, FOLDER_CONFIG, "viewer.yaml")

    # plot tag (from viewer.yaml)
    tag_plot = ["domain", "graph"]

    # run viewer
    try:
        pypeec.run_viewer_file(
            file_voxel, file_viewer,
            tag_plot=tag_plot,
            plot_mode="qt",
        )
    except Exception:
        sys.exit(1)
    else:
        sys.exit(0)
