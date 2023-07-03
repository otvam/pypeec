"""
Module for checking the data type and content.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import os.path
import numpy as np
from pypeec.error import CheckError


def check_dict(name, data, key_list=None, sub_type=None, can_be_empty=True, can_be_none=False):
    """
    Check a dict.
    """

    # check if none
    if can_be_none and data is None:
        return

    # check type
    if not isinstance(data, dict):
        raise CheckError("%s: should be a dict" % name)
    if (not can_be_empty) and (len(data) == 0):
        raise CheckError("%s: should not be empty" % name)

    # check value
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


def check_list(name, data, sub_type=None, can_be_empty=True, can_be_none=False):
    """
    Check a list.
    """

    # check if none
    if can_be_none and data is None:
        return

    # check type
    if not isinstance(data, list):
        raise CheckError("%s: should be a list" % name)
    if (not can_be_empty) and (len(data) == 0):
        raise CheckError("%s: should not be empty" % name)

    # check value
    for value in data:
        if (sub_type is not None) and not isinstance(value, sub_type):
            raise CheckError("%s: invalid type" % name)


def check_float_pts(name, data, size=None, is_positive=False, can_be_zero=True, can_be_empty=True, can_be_none=False):
    """
    Check a 2D float array.
    """

    # check if none
    if can_be_none and data is None:
        return

    # cast to array
    data = np.array(data)

    # check type and value
    if (not can_be_empty) and (len(data) == 0):
        raise CheckError("%s: cannot be empty" % name)
    for data_tmp in data:
        check_float_array(name, data_tmp, size, is_positive, can_be_zero, can_be_empty)


def check_integer_pts(name, data, size=None, is_positive=False, can_be_zero=True, can_be_empty=True, can_be_none=False):
    """
    Check a 2D integer array.
    """

    # check if none
    if can_be_none and data is None:
        return

    # cast to array
    data = np.array(data)

    # check type and value
    if (not can_be_empty) and (len(data) == 0):
        raise CheckError("%s: cannot be empty" % name)
    for data_tmp in data:
        check_integer_array(name, data_tmp, size, is_positive, can_be_zero, can_be_empty)


def check_float_array(name, data, size=None, is_positive=False, can_be_zero=True, can_be_empty=True, can_be_none=False):
    """
    Check a float array.
    """

    # check if none
    if can_be_none and data is None:
        return

    # cast to array
    data = np.array(data)

    # check type and value
    if len(data.shape) != 1:
        raise CheckError("%s: invalid shape" % name)
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


def check_integer_array(name, data, size=None, is_positive=False, can_be_zero=True, can_be_empty=True, can_be_none=False):
    """
    Check an integer array.
    """

    # check if none
    if can_be_none and data is None:
        return

    # cast to array
    data = np.array(data)

    # check type and value
    if len(data.shape) != 1:
        raise CheckError("%s: invalid shape" % name)
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


def check_index_array(name, data, size=None, bnd=None, can_be_empty=True, can_be_none=False):
    """
    Check an integer array.
    """

    # check if none
    if can_be_none and data is None:
        return

    # cast to array
    data = np.array(data)

    # check type and value
    if len(data.shape) != 1:
        raise CheckError("%s: invalid shape" % name)
    if size is not None:
        if not (len(data) == size):
            raise CheckError("%s: invalid array size" % name)
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


def check_float(name, data, is_positive=False, can_be_zero=True, can_be_none=False):
    """
    Check a float.
    """

    # check if none
    if can_be_none and data is None:
        return

    # check type
    if not np.issubdtype(type(data), np.floating):
        raise CheckError("%s: should be a float" % name)

    # check value
    if is_positive and not (data >= 0):
        raise CheckError("%s: should be positive" % name)
    if (not can_be_zero) and (data == 0):
        raise CheckError("%s: cannot be zero" % name)


def check_integer(name, data, is_positive=False, can_be_zero=True, can_be_none=False):
    """
    Check a integer.
    """

    # check if none
    if can_be_none and data is None:
        return

    # check type
    if not np.issubdtype(type(data), np.integer):
        raise CheckError("%s: should be an integer" % name)

    # check value
    if is_positive and not (data >= 0):
        raise CheckError("%s: should be positive" % name)
    if (not can_be_zero) and (data == 0):
        raise CheckError("%s: cannot be zero" % name)


def check_boolean(name, data, can_be_none=False):
    """
    Check a boolean.
    """

    # check if none
    if can_be_none and data is None:
        return

    # check type
    if not isinstance(data, bool):
        raise CheckError("%s: should be a boolean" % name)


def check_string(name, data, can_be_empty=True, can_be_none=False):
    """
    Check a string.
    """

    # check if none
    if can_be_none and data is None:
        return

    # check type
    if not isinstance(data, str):
        raise CheckError("%s: should be a string" % name)
    if (not can_be_empty) and (len(data) == 0):
        raise CheckError("%s: cannot be empty" % name)


def check_choice(name, data, choice_list, can_be_none=False):
    """
    Check a string within given choices.
    """

    # check if none
    if can_be_none and data is None:
        return

    # check type
    if not isinstance(data, str):
        raise CheckError("%s: should be a string" % name)
    if data not in choice_list:
        raise CheckError("%s: invalid value: %s" % (name, data))


def check_folder(name, folder, can_be_none=False):
    """
    Check that a folder is existing.
    """

    # check if none
    if can_be_none and folder is None:
        return

    # check the type
    if not isinstance(folder, str):
        raise CheckError("%s: folder name should be a string" % name)

    # check that the folder exist
    if not os.path.isdir(folder):
        raise CheckError("%s: folder does not exist: %s" % (name, folder))


def check_filename(name, filename, can_be_none=False):
    """
    Check that a filename is existing.
    """

    # check if none
    if can_be_none and filename is None:
        return

    # check the type
    if not isinstance(filename, str):
        raise CheckError("%s: file name should be a string" % name)

    # check that the file exist
    if not os.path.isfile(filename):
        raise CheckError("%s: file does not exist: %s" % (name, filename))

    return filename


def check_assert(name, cond, msg):
    """
    Check an assertion.
    """

    if not cond:
        raise CheckError("%s: %s" % (name, msg))
