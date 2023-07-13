"""
Module for running the PyPEEC workflow.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import os.path
import pickle
import tempfile
import logging
from pypeec import main

# disable logging to prevent clutter during test evaluation
logging.disable(logging.INFO)

# get the path the folder
PATH_ROOT = os.path.dirname(__file__)

# construct the config folder path
FOLDER_CONFIG = os.path.join(PATH_ROOT, "..", "examples", "config")
PATH_EXAMPLES = os.path.join(PATH_ROOT, "..", "examples")


def _create_temp_file():
    """
    Get a temporary file.
    """

    (_, filename) = tempfile.mkstemp(suffix=".pck")

    return filename


def _delete_temp_file(filename):
    """
    Delete a temporary file.
    """

    try:
        os.remove(filename)
    except OSError:
        pass


def run_workflow(folder, name):
    """
    Run the complete workflow:
        - run the mesher
        - run the viewer
        - run the solver
        - run the plotter

    The intermediate file are stored with temporary files.
    """

    # get input file name
    file_geometry = os.path.join(PATH_EXAMPLES, folder, name, "geometry.yaml")
    file_point = os.path.join(PATH_EXAMPLES, folder, name, "point.yaml")
    file_problem = os.path.join(PATH_EXAMPLES, folder, name, "problem.yaml")

    # get config file name
    file_plotter = os.path.join(FOLDER_CONFIG, "plotter.yaml")
    file_viewer = os.path.join(FOLDER_CONFIG, "viewer.yaml")
    file_tolerance = os.path.join(FOLDER_CONFIG, "tolerance.yaml")

    # get the temporary files
    file_voxel = _create_temp_file()
    file_solution = _create_temp_file()

    # run the code
    try:
        # run the mesher
        (status, ex) = main.run_mesher_file(file_geometry, file_voxel, is_truncated=False)
        if not status:
            raise ex

        # load the voxel file
        with open(file_voxel, "rb") as fid:
            data_voxel = pickle.load(fid)

        # run the viewer
        (status, ex) = main.run_viewer_file(file_voxel, file_point, file_viewer, plot_mode="none")
        if not status:
            raise ex

        # run the solver
        (status, ex) = main.run_solver_file(file_voxel, file_problem, file_tolerance, file_solution, is_truncated=False)
        if not status:
            raise ex

        # run the plotter
        (status, ex) = main.run_plotter_file(file_solution, file_point, file_plotter, plot_mode="none")
        if not status:
            raise ex

        # load the solution file
        with open(file_solution, "rb") as fid:
            data_solution = pickle.load(fid)
    finally:
        # close the temporary files
        _delete_temp_file(file_voxel)
        _delete_temp_file(file_solution)

    return data_voxel, data_solution
