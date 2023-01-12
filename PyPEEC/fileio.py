"""
Simple module for serialization and deserialization.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import sys
import json
import pickle
from PyPEEC.lib_shared import logging_utils

# get a logger
logger = logging_utils.get_logger("fileio")


def load_pickle(filename):
    """
    Load a picke file.
    """

    try:
        with open(filename, "rb") as fid:
            data = pickle.load(fid)
    except FileNotFoundError:
        logger.error("file not found: %s" % filename)
        sys.exit(1)

    return data


def load_json(filename):
    """
    Load a JSON file.
    """

    try:
        with open(filename, 'r') as fid:
            data = json.load(fid)
    except FileNotFoundError:
        logger.error("cannot open the file: %s" % filename)
        sys.exit(1)

    return data


def write_pickle(status, filename, data):
    """
    Write a pickle file.
    """

    if status:
        try:
            with open(filename, "wb") as fid:
                pickle.dump(data, fid)
        except FileNotFoundError:
            logger.error("cannot write the file: %s" % filename)
            sys.exit(1)
