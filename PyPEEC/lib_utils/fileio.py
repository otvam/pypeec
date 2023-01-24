"""
Simple module for serialization and deserialization.

WARNING: Pickling data is not secure.
         Only load pickle files that you trust.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import json
import pickle
from PyPEEC.lib_utils.error import FileError


def load_pickle(filename):
    """
    Load a pickle file.
    """

    try:
        with open(filename, "rb") as fid:
            data = pickle.load(fid)
    except (FileNotFoundError, EOFError):
        raise FileError("file not found: %s" % filename)

    return data


def load_json(filename):
    """
    Load a JSON file.
    """

    try:
        with open(filename, 'r') as fid:
            data = json.load(fid)
    except FileNotFoundError:
        raise FileError("cannot open the file: %s" % filename)
    except ValueError:
        raise FileError("invalid JSON file: %s" % filename)

    return data


def write_pickle(filename, data):
    """
    Write a pickle file.
    """

    try:
        with open(filename, "wb") as fid:
            pickle.dump(data, fid)
    except FileNotFoundError:
        raise FileError("cannot write the file: %s" % filename)
