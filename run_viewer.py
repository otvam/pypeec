"""
User script for visualizing a 3D voxel structure.
Contain the program entry point.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import sys

from PyPEEC import viewer


if __name__ == "__main__":
    # get the data
    from data_input import data_solver_simple
    from data_input import data_viewer
    data_voxel = data_solver_simple.get_data_voxel()
    data_viewer = data_viewer.get_data()

    # call lib_plotter
    exit_code = viewer.run(data_voxel, data_viewer)

    # run
    sys.exit(exit_code)
