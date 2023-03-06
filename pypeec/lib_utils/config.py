"""
Configuration of the program.
Defined with global variables.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import os
import sys
import importlib.util
import importlib.resources
import numpy as np
from pypeec.lib_utils import fileio
from pypeec.lib_utils import datachecker
from pypeec.lib_utils.error import FileError, CheckError


class _dict_to_attributes(dict):
    """
    Wrapper to access dict with dot notation.
    """

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def _update_data(data):
    """
    Parse and complete the config.
    """

    # get the GPU usage
    if data["FFT_LIBRARY"] == "SciPy":
        data["USE_FFT_GPU"] = False
    elif data["FFT_LIBRARY"] == "FFTE":
        data["USE_FFT_GPU"] = False
    elif data["FFT_LIBRARY"] == "CuPy":
        data["USE_FFT_GPU"] = True
    else:
        raise ValueError("invalid FFT library")

    # get the number of cores
    if data["FFT_OPTIONS"]["FFTS_WORKER"] is None:
        data["FFT_OPTIONS"]["FFTS_WORKER"] = os.cpu_count()
    if data["FFT_OPTIONS"]["FFTW_THREAD"] is None:
        data["FFT_OPTIONS"]["FFTW_THREAD"] = os.cpu_count()

    # get the data types
    if data["USE_DOUBLE"]:
        data["NP_TYPES"] = {
            "INT": np.int_, "FLOAT": np.float_, "COMPLEX": np.complex_,
            "DINT": np.int_, "DFLOAT": np.float_, "DCOMPLEX": np.complex_,
        }
    else:
        data["NP_TYPES"] = {
            "INT": np.intc, "FLOAT": np.single, "COMPLEX": np.csingle,
            "DINT": np.int_, "DFLOAT": np.float_, "DCOMPLEX": np.complex_,
        }

    # access with dot notation
    data["NP_TYPES"] = _dict_to_attributes(data["NP_TYPES"])
    data["FFT_OPTIONS"] = _dict_to_attributes(data["FFT_OPTIONS"])
    data["LOGGING_OPTIONS"] = _dict_to_attributes(data["LOGGING_OPTIONS"])

    return data


def _check_data(data):
    """
    Check that the config is valid.
    """

    # check type
    key_list = [
        "LOGGING_OPTIONS",
        "FFT_OPTIONS",
        "FFT_LIBRARY",
        "MATRIX_FACTORIZATION",
        "MATRIX_MULTIPLICATION",
        "PAUSE_GUI",
    ]
    datachecker.check_dict("data", data, key_list=key_list)

    # check logging options
    datachecker.check_string("FORMAT", data["LOGGING_OPTIONS"]["FORMAT"])
    datachecker.check_string("LEVEL", data["LOGGING_OPTIONS"]["LEVEL"])
    datachecker.check_integer("INDENTATION", data["LOGGING_OPTIONS"]["INDENTATION"])
    datachecker.check_boolean("EXCEPTION_TRACE", data["LOGGING_OPTIONS"]["EXCEPTION_TRACE"])
    datachecker.check_boolean("USE_COLOR", data["LOGGING_OPTIONS"]["USE_COLOR"])
    datachecker.check_string("CL_DEBUG", data["LOGGING_OPTIONS"]["CL_DEBUG"])
    datachecker.check_string("CL_INFO", data["LOGGING_OPTIONS"]["CL_INFO"])
    datachecker.check_string("CL_WARNING", data["LOGGING_OPTIONS"]["CL_WARNING"])
    datachecker.check_string("CL_ERROR", data["LOGGING_OPTIONS"]["CL_ERROR"])
    datachecker.check_string("CL_CRITICAL", data["LOGGING_OPTIONS"]["CL_CRITICAL"])
    datachecker.check_string("CL_RESET", data["LOGGING_OPTIONS"]["CL_RESET"])

    # check FFT options
    if data["FFT_OPTIONS"]["FFTS_WORKER"] is not None:
        datachecker.check_integer("FFTS_WORKER", data["FFT_OPTIONS"]["FFTS_WORKER"])
    if data["FFT_OPTIONS"]["FFTW_THREAD"] is not None:
        datachecker.check_integer("FFTW_THREAD", data["FFT_OPTIONS"]["FFTW_THREAD"])
    datachecker.check_integer("FFTW_BYTE_ALIGN", data["FFT_OPTIONS"]["FFTW_BYTE_ALIGN"])
    datachecker.check_float("FFTW_CACHE_TIMEOUT", data["FFT_OPTIONS"]["FFTW_CACHE_TIMEOUT"])

    # check other switches
    datachecker.check_boolean("USE_DOUBLE", data["USE_DOUBLE"])
    datachecker.check_float("PAUSE_GUI", data["PAUSE_GUI"])
    datachecker.check_choice("FFT_LIBRARY", data["FFT_LIBRARY"], ["SciPy", "FFTW", "CuPy"])
    datachecker.check_choice("MATRIX_FACTORIZATION", data["MATRIX_FACTORIZATION"], ["SuperLU", "UMFPACK"])
    datachecker.check_choice("MATRIX_MULTIPLICATION", data["MATRIX_MULTIPLICATION"], ["FFT", "DIRECT"])


def _check_lib(data):
    """
    Check that the required libraries are installed.
    """

    # check GPU
    if data["FFT_LIBRARY"] == "SciPy":
        lib = importlib.util.find_spec("scipy")
        if lib is None:
            raise FileError("Library SciPy is not installed and is activated in the config")
    elif data["FFT_LIBRARY"] == "FFTW":
            lib = importlib.util.find_spec("pyfftw")
            if lib is None:
                raise FileError("Library FFTW is not installed and is activated in the config")
    elif data["FFT_LIBRARY"] == "CuPy":
        lib = importlib.util.find_spec("cupy")
        if lib is None:
            raise FileError("Library CuPy is not installed and is activated in the config")
    else:
        raise ValueError("invalid FFT library")


def set_config(file_config):
    """
    Load a config file and store the data in global variables.
    """

    # parse the file
    data = fileio.load_config(file_config)

    # check the data integrity
    _check_data(data)

    # check that the libraries are installed
    _check_lib(data)

    # update the configuration
    data = _update_data(data)

    # assign data to global variables
    for key in data:
        globals()[key] = data[key]


# init data to global variables
LOGGING_OPTIONS = dict()
FFT_OPTIONS = dict()
FFT_LIBRARY = None
MATRIX_FACTORIZATION = None
MATRIX_MULTIPLICATION = None
PAUSE_GUI = None
USE_DOUBLE = None
NP_TYPES = None
USE_FFT_GPU = None

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
