"""
Configuration of the program.
Defined with global variables.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import sys
import importlib.resources
from PyPEEC.lib_utils import fileio
from PyPEEC.lib_utils.error import FileError


def set_config(file_config):
    """
    Load a config file and store the data in global variables.
    """

    # parse the file
    data = fileio.load_config(file_config)

    # call the global variables
    global LOGGING_OPTIONS
    global MATRIX_FACTORIZATION
    global MATRIX_MULTIPLICATION
    global FFT_OPTIONS

    # assign data
    LOGGING_OPTIONS = data["LOGGING_OPTIONS"]
    MATRIX_FACTORIZATION = data["MATRIX_FACTORIZATION"]
    MATRIX_MULTIPLICATION = data["MATRIX_MULTIPLICATION"]
    FFT_OPTIONS = data["FFT_OPTIONS"]


# init the global variables
LOGGING_OPTIONS = None
MATRIX_FACTORIZATION = None
MATRIX_MULTIPLICATION = None
FFT_OPTIONS = None

# get the default config file
default_file_config = importlib.resources.files("PyPEEC").joinpath("pypeec.yaml")

# load the default config files
try:
    set_config(default_file_config)
except FileError as ex:
    print("INVALID CONFIGURATION FILE")
    print("==========================")
    print(str(ex))
    print("==========================")
    print("EXIT")
    sys.exit(1)