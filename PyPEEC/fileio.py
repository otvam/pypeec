"""
Simple module for serialization and deserialization.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import sys
import json
import pickle


def load_pickle(filename):
    """
    Load a picke file.
    """

    try:
        with open(filename, "rb") as fid:
            data = pickle.load(fid)
    except FileNotFoundError:
        print("file not found: %s" % filename)
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
        print("cannot open the file: %s" % filename)
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
            print("cannot write the file: %s" % filename)
            sys.exit(1)
