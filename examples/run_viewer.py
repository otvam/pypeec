"""
User script for visualizing a 3D voxel structure.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import sys
import os.path
from pypeec import main
from examples import examples_config

# get config
PATH_ROOT = examples_config.PATH_ROOT
EXAMPLE_NAME = examples_config.EXAMPLE_NAME


if __name__ == "__main__":
    # get the filename
    file_voxel = os.path.join(PATH_ROOT, EXAMPLE_NAME, "voxel.pck")
    file_point = os.path.join(PATH_ROOT, EXAMPLE_NAME, "point.yaml")
    file_viewer = os.path.join(PATH_ROOT, "config", "viewer.json")

    # run viewer
    (status, ex) = main.run_viewer(file_voxel, file_point, file_viewer)
    sys.exit(int(not status))
