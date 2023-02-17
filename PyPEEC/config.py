"""
Configuration of the program.
Defined with global variables.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import sys
import pathlib
import importlib.resources as resources
from PyPEEC.lib_utils import fileio
from PyPEEC.lib_utils.error import FileError


def get_config(filename):
    try:
        data = fileio.load_yaml(filename)
    except FileError as ex:
        print("INVALID CONFIGURATION FILE")
        print("==========================")
        print(str(ex))
        print("==========================")
        print("EXIT")
        sys.exit(1)

    return data


# get the file name
filename_user = pathlib.Path("config.yaml")
filename_default = resources.files("PyPEEC").joinpath("config.yaml")

# load the config
if filename_user.is_file():
    data = get_config(filename_user)
elif filename_default.is_file():
    data = get_config(filename_default)
else:
    print("INVALID CONFIGURATION FILE")
    print("==========================")
    print("file not found")
    print("==========================")
    print("EXIT")
    sys.exit(1)

# assign data
LOGGING_OPTIONS = data["LOGGING_OPTIONS"]
MATRIX_FACTORIZATION = data["MATRIX_FACTORIZATION"]
MATRIX_MULTIPLICATION = data["MATRIX_MULTIPLICATION"]
FFT_OPTIONS = data["FFT_OPTIONS"]
