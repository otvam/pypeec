"""
User script for meshing a voxel structure.
Contain the program entry point.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import os
import sys
from PyPEEC import script


if __name__ == "__main__":
    # name of the simulation
    # name = "png_inductor"
    # name = "stl_inductor"
    # name = "voxel_slab"
    name = "voxel_transformer"

    # get the filename
    file_mesher = os.path.join("data_input_mesher", name + ".json")
    file_voxel = os.path.join("data_output_voxel",  name + ".pck")

    # run
    status = script.run_mesher(file_mesher, file_voxel)
    sys.exit(int(not status))
