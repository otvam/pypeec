"""
Simple module for serialization and deserialization.

WARNING: Pickling data is not secure.
         Only load pickle files that you trust.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import os
import json
import pickle
import yaml
from PyPEEC.lib_utils.error import FileError


def load_yaml(filename):
    """
    Load a YAML file.
    """

    try:
        with open(filename, 'r') as fid:
            data = yaml.safe_load(fid)
    except FileNotFoundError:
        raise FileError("cannot open the file: %s" % filename)
    except yaml.YAMLError as ex:
        raise FileError("invalid YAML file: %s\n%s" % (filename, str(ex)))

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
    except json.JSONDecodeError as ex:
        raise FileError("invalid JSON file: %s\n%s" % (filename, str(ex)))

    return data


def load_config(filename):
    """
    Load a config file (JSON or YAML).
    """

    # check extension
    (name, ext) = os.path.splitext(filename)
    if ext in [".json", ".js"]:
        data = load_json(filename)
    elif ext in [".yaml", ".yml"]:
        data = load_yaml(filename)
    else:
        raise FileError("invalid file extension: %s" % filename)

    return data


def load_pickle(filename):
    """
    Load a pickle file.
    """

    # check extension
    (name, ext) = os.path.splitext(filename)
    if ext != ".pck":
        raise FileError("invalid file extension: %s" % filename)

    # load the Pickle file
    try:
        with open(filename, "rb") as fid:
            data = pickle.load(fid)
    except pickle.UnpicklingError:
        raise FileError("invalid Pickle file: %s" % filename)
    except EOFError:
        raise FileError("file not found: %s" % filename)
    except FileNotFoundError:
        raise FileError("invalid Pickle file: %s" % filename)

    return data


def write_pickle(filename, data):
    """
    Write a pickle file.
    """

    # check extension
    (name, ext) = os.path.splitext(filename)
    if ext != ".pck":
        raise FileError("invalid file extension: %s" % filename)

    try:
        with open(filename, "wb") as fid:
            pickle.dump(data, fid)
    except pickle.PicklingError:
        raise FileError("invalid data for Pickle: %s" % filename)
    except FileNotFoundError:
        raise FileError("cannot write the file: %s" % filename)
