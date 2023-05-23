"""
User script for visualizing a 3D voxel structure.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import sys
import os.path
from pypeec import main
from pypeec import config
from examples import examples_config

# get config
PATH_ROOT = examples_config.PATH_ROOT
CFG_PYPEEC = examples_config.CFG_PYPEEC
CFG_PLOT = examples_config.CFG_PLOT
FOLDER_NAME = examples_config.FOLDER_NAME
EXAMPLE_NAME = examples_config.EXAMPLE_NAME


if __name__ == "__main__":
    # get the filenames
    file_voxel = os.path.join(PATH_ROOT, FOLDER_NAME, EXAMPLE_NAME, "voxel.pck")
    file_point = os.path.join(PATH_ROOT, FOLDER_NAME, EXAMPLE_NAME, "point.yaml")
    file_config = os.path.join(PATH_ROOT, CFG_PYPEEC, "configuration.yaml")
    file_viewer = os.path.join(PATH_ROOT, CFG_PLOT, "viewer.json")

    # set config
    config.set_config(file_config)

    # run viewer
    (status, ex) = main.run_viewer_file(file_voxel, file_point, file_viewer)
    sys.exit(int(not status))
