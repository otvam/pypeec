"""
Module for checking the data type and content.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import numpy as np
from pypeec.error import CheckError


def check_dict(name, data, key_list=None, sub_type=None, can_be_empty=True):
    """
    Check a dict.
    """

    if not isinstance(data, dict):
        raise CheckError("%s: should be a dict" % name)
    if (not can_be_empty) and (len(data) == 0):
        raise CheckError("%s: should not be empty" % name)
    for tag, value in data.items():
        if not isinstance(tag, str):
            raise CheckError("%s: all the keys should be strings" % name)
        if len(tag) == 0:
            raise CheckError("%s: keys cannot be empty" % name)
        if (sub_type is not None) and not isinstance(value, sub_type):
            raise CheckError("%s: invalid type" % name)
    if key_list is not None:
        for tag in key_list:
            if tag not in data:
                raise CheckError("%s: dict is incomplete: %s" % (name, tag))


def check_list(name, data, sub_type=None, can_be_empty=True):
    """
    Check a list.
    """

    if not isinstance(data, list):
        raise CheckError("%s: should be a list" % name)
    if (not can_be_empty) and (len(data) == 0):
        raise CheckError("%s: should not be empty" % name)
    for value in data:
        if (sub_type is not None) and not isinstance(value, sub_type):
            raise CheckError("%s: invalid type" % name)


def check_float_array(name, data, size=None, is_positive=False, can_be_zero=True, can_be_empty=True):
    """
    Check a float array.
    """

    data = np.array(data)
    if size is not None:
        if not (len(data) == size):
            raise CheckError("%s: invalid array size" % name)
    if (not can_be_empty) and (len(data) == 0):
        raise CheckError("%s: cannot be empty" % name)
    if len(data) > 0:
        if not np.issubdtype(data.dtype, np.floating):
            raise CheckError("%s: invalid array type" % name)
        if is_positive and not np.all(data >= 0):
            raise CheckError("%s: should be positive" % name)
        if (not can_be_zero) and np.any(data == 0):
            raise CheckError("%s: cannot be zero" % name)


def check_integer_array(name, data, size=None, is_positive=False, can_be_zero=True, can_be_empty=True):
    """
    Check an integer array.
    """

    data = np.array(data)
    if size is not None:
        if not (len(data) == size):
            raise CheckError("%s: invalid array size" % name)
    if (not can_be_empty) and (len(data) == 0):
        raise CheckError("%s: cannot be empty" % name)
    if len(data) > 0:
        if not np.issubdtype(data.dtype, np.integer):
            raise CheckError("%s: invalid array type" % name)
        if is_positive and not np.all(data >= 0):
            raise CheckError("%s: should be positive" % name)
        if (not can_be_zero) and np.any(data == 0):
            raise CheckError("%s: cannot be zero" % name)


def check_index_array(name, data, bnd=None, can_be_empty=True):
    """
    Check an integer array.
    """

    data = np.array(data)
    if (not can_be_empty) and (len(data) == 0):
        raise CheckError("%s: cannot be empty" % name)
    if len(data) > 0:
        if not np.issubdtype(data.dtype, np.integer):
            raise CheckError("%s: invalid array type" % name)
        if not (len(np.unique(data)) == len(data)):
            raise CheckError("%s: indices should be unique" % name)
        if bnd is not None:
            if not (np.all(data >= 0) and np.all(data < bnd)):
                raise CheckError("%s: invalid index range" % name)


def check_float(name, data, is_positive=False, can_be_zero=True):
    """
    Check a float.
    """

    if not np.issubdtype(type(data), np.floating):
        raise CheckError("%s: should be a float" % name)
    if is_positive and not (data >= 0):
        raise CheckError("%s: should be positive" % name)
    if (not can_be_zero) and (data == 0):
        raise CheckError("%s: cannot be zero" % name)


def check_integer(name, data, is_positive=False, can_be_zero=True):
    """
    Check a integer.
    """

    if not np.issubdtype(type(data), np.integer):
        raise CheckError("%s: should be an integer" % name)
    if is_positive and not (data >= 0):
        raise CheckError("%s: should be positive" % name)
    if (not can_be_zero) and (data == 0):
        raise CheckError("%s: cannot be zero" % name)


def check_boolean(name, data):
    """
    Check a boolean.
    """

    if not isinstance(data, bool):
        raise CheckError("%s: should be a boolean" % name)


def check_string(name, data, can_be_empty=True):
    """
    Check a string.
    """

    if not isinstance(data, str):
        raise CheckError("%s: should be a string" % name)
    if (not can_be_empty) and (len(data) == 0):
        raise CheckError("%s: cannot be empty" % name)


def check_choice(name, data, choice_list):
    """
    Check a string within given choices.
    """

    if not isinstance(data, str):
        raise CheckError("%s: should be a string" % name)
    if data not in choice_list:
        raise CheckError("%s: invalid value: %s" % (name, data))


def check_filename(name, filename):
    """
    Check that a filename is existing.
    """

    # check the type
    if not isinstance(filename, str):
        raise CheckError("%s: file name should be a string" % name)

    # check that the file exist
    try:
        fid = open(filename, "rb")
        fid.close()
    except FileNotFoundError:
        raise CheckError("%s: file does not exist: %s" % (name, filename))

    return filename


def check_assert(name, cond, msg):
    """
    Check an assertion.
    """

    if not cond:
        raise CheckError("%s: %s" % (name, msg))
