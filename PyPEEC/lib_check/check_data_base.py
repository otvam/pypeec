"""
Module for checking the data type and content.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import numpy as np
from PyPEEC.lib_utils.error import CheckError


def check_dict(name, data, str_key, key_list):
    """
    Check a dict.
    """

    if not isinstance(data, dict):
        raise CheckError("%s: should be a dict" % name)
    for tag in data:
        if str_key and not isinstance(tag, str):
            raise CheckError("%s: all the keys should be strings" % name)
    if key_list is not None:
        for tag in key_list:
            if tag not in data:
                raise CheckError("%s: dict is incomplete" % name)


def check_list(name, data, can_be_empty):
    """
    Check a list.
    """

    if not isinstance(data, list):
        raise CheckError("%s: should be a list" % name)
    if (not can_be_empty) and (len(data) == 0):
        raise CheckError("%s: should not be empty" % name)


def check_float_array(name, data, size, is_positive, can_be_zero):
    """
    Check an float array.
    """

    data = np.array(data)
    if not (len(data) == size):
        raise CheckError("%s: invalid array size" % name)
    if not np.issubdtype(data.dtype, np.floating):
        raise CheckError("%s: invalid array type" % name)
    if is_positive and not np.all(data > 0):
        raise CheckError("%s: should be positive" % name)
    if (not can_be_zero) and np.any(data == 0):
        raise CheckError("%s: cannot be zero" % name)


def check_float(name, data, is_positive, can_be_zero):
    """
    Check a float.
    """

    if not np.issubdtype(type(data), np.floating):
        raise CheckError("%s: should be a float" % name)
    if is_positive and not (data > 0):
        raise CheckError("%s: should be positive" % name)
    if (not can_be_zero) and (data == 0):
        raise CheckError("%s: cannot be zero" % name)


def check_integer(name, data, is_positive, can_be_zero):
    """
    Check a integer.
    """

    if not np.issubdtype(type(data), np.integer):
        raise CheckError("%s: should be an integer" % name)
    if is_positive and not (data > 0):
        raise CheckError("%s: should be positive" % name)
    if (not can_be_zero) and (data == 0):
        raise CheckError("%s: cannot be zero" % name)


def check_boolean(name, data):
    """
    Check a integer.
    """

    if not isinstance(data, bool):
        raise CheckError("%s: should be a boolean" % name)
