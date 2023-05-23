"""
User script for meshing a voxel structure.
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
FOLDER_NAME = examples_config.FOLDER_NAME
EXAMPLE_NAME = examples_config.EXAMPLE_NAME


if __name__ == "__main__":
    # get the filenames
    file_geometry = os.path.join(PATH_ROOT, FOLDER_NAME, EXAMPLE_NAME, "geometry.yaml")
    file_voxel = os.path.join(PATH_ROOT, FOLDER_NAME, EXAMPLE_NAME, "voxel.pck")
    file_config = os.path.join(PATH_ROOT, CFG_PYPEEC, "configuration.yaml")

    # set config
    config.set_config(file_config)

    # run
    (status, ex) = main.run_mesher_file(file_geometry, file_voxel)
    sys.exit(int(not status))
