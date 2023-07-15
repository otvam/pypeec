"""
User script for meshing a voxel structure.
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
    file_geometry = os.path.join(PATH_ROOT, FOLDER_NAME, EXAMPLE_NAME, "geometry.yaml")
    file_voxel = os.path.join(PATH_ROOT, FOLDER_NAME, EXAMPLE_NAME, "voxel.pck")

    # run
    (status, ex) = main.run_mesher_file(file_geometry, file_voxel)
    sys.exit(int(not status))
