"""
Module for getting/reading/writing the test data.

Load the test configuration file.
Read the prescribed test results.
Write the prescribed test results.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import os.path
import datetime
import json

# get the path the folder
PATH_ROOT = os.path.dirname(__file__)


def write_results(folder, name, mesher, solver):
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


def read_results(folder, name):
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
