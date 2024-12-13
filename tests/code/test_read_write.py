"""
Module for reading and writing the test data.

Read the prescribed test results.
Write the prescribed test results.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import os.path
import datetime
import scilogger
import scisave

# disable logging
scilogger.disable()

# get the path the folder
PATH_ROOT = os.path.dirname(__file__)


def write_results(name, mesher, solver):
    """
    Write the file containing the prescribed test results.
    """

    # get timestamp
    timestamp = str(datetime.datetime.now())

    # get metadata
    metadata = {
        "name": name,
        "timestamp": timestamp,
    }

    # assemble results
    data_test = {"metadata": metadata, "mesher": mesher, "solver": solver}

    # write the file containing the test results
    file_test = os.path.join(PATH_ROOT, "..", "data", name + ".json")
    scisave.write_data(file_test, data_test)


def read_results(name):
    """
    Load the file containing the prescribed test results.
    """

    # load the file containing the test results
    file_test = os.path.join(PATH_ROOT, "..", "data", name + ".json")
    data_test = scisave.load_data(file_test)

    # extract results
    mesher = data_test["mesher"]
    solver = data_test["solver"]

    return mesher, solver
