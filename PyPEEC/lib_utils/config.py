"""
Configuration of the program.
Defined with global variables.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import sys
import importlib.util
import importlib.resources
from PyPEEC.lib_utils import fileio
from PyPEEC.lib_utils.error import FileError, CheckError


def _check_data():
    """
    Check that the config is valid.
    """

    pass


def _check_lib():
    """
    Check that the required libraries are installed.
    """

    # check GPU
    if USE_GPU:
        lib = importlib.util.find_spec("cupy")
        if lib is None:
            raise FileError("Library CuPy is not installed and is activated in the config")

    # check FFTW
    if FFT_LIBRARY == "FFTW":
        lib = importlib.util.find_spec("pyfftw")
        if lib is None:
            raise FileError("Library FFTW is not installed and is activated in the config")

    # check library
    if FFT_LIBRARY == "UMFPACK":
        lib = importlib.util.find_spec("scikits.umfpack")
        if lib is None:
            raise FileError("Library UMFPACK is not installed and is activated in the config")


def set_config(file_config):
    """
    Load a config file and store the data in global variables.
    """

    # name of the global variables
    var = [
        "LOGGING_OPTIONS",
        "MATRIX_FACTORIZATION",
        "MATRIX_MULTIPLICATION",
        "FFT_LIBRARY",
        "FFT_OPTIONS",
        "USE_GPU",
    ]

    # parse the file
    data = fileio.load_config(file_config)

    # assign data to global variables
    for name in var:
        if name not in data:
            raise FileError("invalid configuration: field is missing: %s" % name)
        else:
            globals()[name] = data[name]

    # check the data integrity
    _check_data()

    # check that the libraries are installed
    _check_lib()


# init data to global variables
LOGGING_OPTIONS = None
MATRIX_FACTORIZATION = None
MATRIX_MULTIPLICATION = None
FFT_LIBRARY = None
FFT_OPTIONS = None
USE_GPU = None

# load the default config files
try:
    with importlib.resources.path("PyPEEC", "pypeec.yaml") as default_file_config:
        set_config(default_file_config)
except (FileError, CheckError) as ex:
    print("INVALID CONFIGURATION FILE")
    print("==========================")
    print(str(ex))
    print("==========================")
    print("EXIT")
    sys.exit(1)
