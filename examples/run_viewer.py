"""
User script for visualizing a 3D voxel structure.
Contain the program entry point.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import os
import sys
from PyPEEC import script
from examples import examples_visualization
from examples import examples_utils
from examples import examples_config

# get config
PATH_ROOT = examples_config.PATH_ROOT
EXAMPLE_NAME = examples_config.EXAMPLE_NAME


if __name__ == "__main__":
    # get the filename
    file_voxel = os.path.join(PATH_ROOT, "data_voxel", EXAMPLE_NAME + ".pck")
    file_viewer = os.path.join(PATH_ROOT, "data_visualization", "data_viewer.json")

    # get viewer data
    data_viewer = examples_visualization.get_data_viewer()

    # create folder and file
    examples_utils.create_folder(file_viewer)
    examples_utils.write_json(file_viewer, data_viewer)

    # run viewer
    status = script.run_viewer(file_voxel, file_viewer, True)
    sys.exit(int(not status))
