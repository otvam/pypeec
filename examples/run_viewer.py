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
from examples import examples_visualization
from examples import examples_config

# get config
PATH_ROOT = examples_config.PATH_ROOT
EXAMPLE_NAME = examples_config.EXAMPLE_NAME


if __name__ == "__main__":
    # get the filename
    file_voxel = os.path.join(PATH_ROOT, EXAMPLE_NAME, "voxel.pck")
    file_point = os.path.join(PATH_ROOT, EXAMPLE_NAME, "point.json")
    file_viewer = os.path.join(PATH_ROOT, "visualization", "data_viewer.json")

    # get viewer data
    data_viewer = examples_visualization.get_data_viewer()

    # create file
    with open(file_viewer, "w") as fid:
        json.dump(data_viewer, fid, indent=4)

    # run viewer
    status = script.run_viewer(file_voxel, file_point, file_viewer, True)
    sys.exit(int(not status))
