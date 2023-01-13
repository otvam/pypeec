"""
Small utils used in the examples files.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import os
import json


def write_json(filename, data):
    """
    Write a JSON file.
    """

    with open(filename, "w") as fid:
        json.dump(data, fid, indent=4)


def create_folder(filename):
    """
    Create a folder (no nothing if exists).
    """

    try:
        os.makedirs(os.path.dirname(filename))
    except FileExistsError:
        pass
