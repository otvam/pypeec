"""
Module for getting/reading/writing the test data.

Load the test configuration file.
Read the prescribed test results.
Write the prescribed test results.
Run the mesher, viewer, solver, and plotter.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import os.path
import datetime
import json
import pickle
import tempfile
import logging
from pypeec import main

# disable logging to prevent clutter during test evaluation
logging.disable(logging.INFO)

# get the path the folder
PATH_ROOT = os.path.dirname(__file__)


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


def write_test_results(folder, name, mesher, solver):
    """
    Write the file containing the prescribed test results.
    """

    # get timestamp
    timestamp = str(datetime.datetime.now())

    # get metadata
    metadata = {
        "folder": folder,
        "name": name,
        "timestamp": timestamp,
    }

    # assemble results
    data_test = {"metadata": metadata, "mesher": mesher, "solver": solver}

    # file containing the test results
    file_test = os.path.join(PATH_ROOT, folder, name + ".json")

    with open(file_test, "w") as fid:
        json.dump(data_test, fid, indent=4)


def read_test_results(folder, name):
    """
    Load the file containing the prescribed test results.
    """

    # file containing the test results
    file_test = os.path.join(PATH_ROOT, folder, name + ".json")

    # load the test results
    with open(file_test, "r") as fid:
        data_test = json.load(fid)

    # extract results
    mesher = data_test["mesher"]
    solver = data_test["solver"]

    return mesher, solver


def get_config():
    """
    Load the test configuration file.
    """

    # file containing the test results
    file_test = os.path.join(PATH_ROOT, "test_config.json")

    # load the test results
    with open(file_test, "r") as fid:
        data_config = json.load(fid)

    # extract results
    tol = data_config["tol"]
    check_test = data_config["check_test"]
    generate_test = data_config["generate_test"]

    return tol, check_test, generate_test


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
    file_geometry = os.path.join(PATH_ROOT, "..", "examples", folder, name, "geometry.yaml")
    file_point = os.path.join(PATH_ROOT, "..", "examples", folder, name, "point.yaml")
    file_problem = os.path.join(PATH_ROOT, "..", "examples", folder, name, "problem.yaml")

    # get config file name
    file_plotter = os.path.join(PATH_ROOT, "..", "examples", "config", "plotter.json")
    file_viewer = os.path.join(PATH_ROOT, "..", "examples", "config", "viewer.json")
    file_tolerance = os.path.join(PATH_ROOT, "..", "examples", "config", "tolerance.json")

    # get the temporary files
    file_voxel = _create_temp_file()
    file_solution = _create_temp_file()

    # run the code
    try:
        # run the mesher
        (status, ex) = main.run_mesher_file(file_geometry, file_voxel)
        if not status:
            raise ex

        # load the voxel file
        with open(file_voxel, "rb") as fid:
            data_voxel = pickle.load(fid)

        # run the viewer
        (status, ex) = main.run_viewer_file(file_voxel, file_point, file_viewer, is_silent=True)
        if not status:
            raise ex

        # run the solver
        (status, ex) = main.run_solver_file(file_voxel, file_problem, file_tolerance, file_solution)
        if not status:
            raise ex

        # run the plotter
        (status, ex) = main.run_plotter_file(file_solution, file_point, file_plotter, is_silent=True)
        if not status:
            raise ex

        # check the solution file
        with open(file_solution, "rb") as fid:
            data_solution = pickle.load(fid)
    finally:
        # close the temporary files
        _delete_temp_file(file_voxel)
        _delete_temp_file(file_solution)

    return data_voxel, data_solution
