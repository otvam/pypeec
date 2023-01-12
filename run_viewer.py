"""
User script for visualizing a 3D voxel structure.
Contain the program entry point.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import os
import sys
from PyPEEC import script


if __name__ == "__main__":
    # name of the simulation
    name = "png_inductor"
    # name = "stl_inductor"
    # name = "test_slab"

    # get the filename
    file_voxel = os.path.join("data_output_voxel",  name + ".pck")
    file_viewer = os.path.join("data_input_plotter_viewer", "data_viewer.json")

    # run viewer
    status = script.run_viewer(file_voxel, file_viewer)
    sys.exit(int(not status))
