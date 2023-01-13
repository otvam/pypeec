"""
User script for meshing a voxel structure.
Contain the program entry point.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import os
import sys
from PyPEEC import script
from examples import config_examples

# get config
PATH_ROOT = config_examples.PATH_ROOT
EXAMPLE_NAME = config_examples.EXAMPLE_NAME


if __name__ == "__main__":
    # get the filename
    file_mesher = os.path.join(PATH_ROOT, "data_mesher", EXAMPLE_NAME + ".json")
    file_voxel = os.path.join(PATH_ROOT, "data_voxel", EXAMPLE_NAME + ".pck")

    # run
    status = script.run_mesher(file_mesher, file_voxel)
    sys.exit(int(not status))
