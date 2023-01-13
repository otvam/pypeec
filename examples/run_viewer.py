"""
User script for visualizing a 3D voxel structure.
Contain the program entry point.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import os
import sys
import json
from PyPEEC import script
from examples import config_viewer_plotter
from examples import config_examples

# get config
PATH_ROOT = config_examples.PATH_ROOT
EXAMPLE_NAME = config_examples.EXAMPLE_NAME


if __name__ == "__main__":
    # get the filename
    file_voxel = os.path.join(PATH_ROOT, "data_voxel", EXAMPLE_NAME + ".pck")
    file_viewer = os.path.join(PATH_ROOT, "data_viewer_plotter", "data_viewer.json")

    # get viewer data
    data_viewer = config_viewer_plotter.get_data_viewer()

    # write file
    with open(file_viewer, "w") as fid:
        json.dump(data_viewer, fid, indent=4)

    # run viewer
    status = script.run_viewer(file_voxel, file_viewer, True)
    sys.exit(int(not status))
