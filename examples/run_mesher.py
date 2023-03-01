"""
User script for meshing a voxel structure.
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
    # get the filenames
    file_mesher = os.path.join(PATH_ROOT, EXAMPLE_NAME, "mesher.yaml")
    file_voxel = os.path.join(PATH_ROOT, EXAMPLE_NAME, "voxel.pck")

    # run
    (status, ex) = main.run_mesher(file_mesher, file_voxel)
    sys.exit(int(not status))
