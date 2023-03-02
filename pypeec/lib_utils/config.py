"""
Configuration of the program.
Defined with global variables.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import sys
import importlib.util
import importlib.resources
from pypeec.lib_utils import fileio
from pypeec.lib_utils import datachecker
from pypeec.lib_utils.error import FileError, CheckError


def _check_data():
    """
    Check that the config is valid.
    """

    # check logging options
    datachecker.check_string("FORMAT", LOGGING_OPTIONS["FORMAT"])
    datachecker.check_string("FORMAT", LOGGING_OPTIONS["FORMAT"])
    datachecker.check_string("LEVEL", LOGGING_OPTIONS["LEVEL"])
    datachecker.check_integer("INDENTATION", LOGGING_OPTIONS["INDENTATION"])
    datachecker.check_boolean("EXCEPTION_TRACE", LOGGING_OPTIONS["EXCEPTION_TRACE"])
    datachecker.check_boolean("USE_COLOR", LOGGING_OPTIONS["USE_COLOR"])
    datachecker.check_string("CL_DEBUG", LOGGING_OPTIONS["CL_DEBUG"])
    datachecker.check_string("CL_INFO", LOGGING_OPTIONS["CL_INFO"])
    datachecker.check_string("CL_WARNING", LOGGING_OPTIONS["CL_WARNING"])
    datachecker.check_string("CL_ERROR", LOGGING_OPTIONS["CL_ERROR"])
    datachecker.check_string("CL_CRITICAL", LOGGING_OPTIONS["CL_CRITICAL"])
    datachecker.check_string("CL_RESET", LOGGING_OPTIONS["CL_RESET"])

    # check FFT options
    if FFT_OPTIONS["FFTS_WORKER"] is not None:
        datachecker.check_integer("FFTS_WORKER", FFT_OPTIONS["FFTS_WORKER"])
    if FFT_OPTIONS["FFTW_THREAD"] is not None:
        datachecker.check_integer("FFTW_THREAD", FFT_OPTIONS["FFTW_THREAD"])
    datachecker.check_integer("FFTW_BYTE_ALIGN", FFT_OPTIONS["FFTW_BYTE_ALIGN"])
    datachecker.check_float("FFTW_CACHE_TIMEOUT", FFT_OPTIONS["FFTW_CACHE_TIMEOUT"])

    # check other switches
    datachecker.check_boolean("USE_GPU", USE_GPU)
    datachecker.check_float("PAUSE_GUI", PAUSE_GUI)
    datachecker.check_choice("FFT_LIBRARY", FFT_LIBRARY, ["SciPy", "FFTW"])
    datachecker.check_choice("MATRIX_FACTORIZATION", MATRIX_FACTORIZATION, ["SuperLU", "UMFPACK"])
    datachecker.check_choice("MATRIX_MULTIPLICATION", MATRIX_MULTIPLICATION, ["FFT", "DIRECT"])


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
    key_list = [
        "LOGGING_OPTIONS",
        "FFT_OPTIONS",
        "FFT_LIBRARY",
        "MATRIX_FACTORIZATION",
        "MATRIX_MULTIPLICATION",
        "PAUSE_GUI",
        "USE_GPU",
    ]

    # parse the file
    data = fileio.load_config(file_config)

    # check type
    datachecker.check_dict("data", data, key_list=key_list)

    # assign data to global variables
    for key in key_list:
        globals()[key] = data[key]

    # check the data integrity
    _check_data()

    # check that the libraries are installed
    _check_lib()


# init data to global variables
LOGGING_OPTIONS = dict()
FFT_OPTIONS = dict()
FFT_LIBRARY = None
MATRIX_FACTORIZATION = None
MATRIX_MULTIPLICATION = None
PAUSE_GUI = None
USE_GPU = None

# load the default config files
try:
    with importlib.resources.path("pypeec", "pypeec.yaml") as default_file_config:
        set_config(default_file_config)
except (FileError, CheckError) as ex:
    print("INVALID CONFIGURATION FILE")
    print("==========================")
    print(str(ex))
    print("==========================")
    print("EXIT")
    sys.exit(1)
