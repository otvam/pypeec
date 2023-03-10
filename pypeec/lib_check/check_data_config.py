"""
Module for checking the solver config data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import importlib.util
import numpy as np
from pypeec.lib_utils import datachecker


def _update_data(data_config):
    """
    Parse and complete the config.
    """

    # get the GPU usage
    if data_config["FFT_LIBRARY"] == "SciPy":
        data_config["USE_FFT_GPU"] = False
    elif data_config["FFT_LIBRARY"] == "FFTW":
        data_config["USE_FFT_GPU"] = False
    elif data_config["FFT_LIBRARY"] == "CuPy":
        data_config["USE_FFT_GPU"] = True
    else:
        raise ValueError("invalid FFT library")

    # get the data types
    if data_config["USE_DOUBLE"]:
        data_config["NP_TYPES"] = {
            "INT": np.int_, "FLOAT": np.float_, "COMPLEX": np.complex_,
            "DINT": np.int_, "DFLOAT": np.float_, "DCOMPLEX": np.complex_,
        }
    else:
        data_config["NP_TYPES"] = {
            "INT": np.intc, "FLOAT": np.single, "COMPLEX": np.csingle,
            "DINT": np.int_, "DFLOAT": np.float_, "DCOMPLEX": np.complex_,
        }

    return data_config


def _check_data(data_config):
    """
    Check that the config is valid.
    """

    # check type
    key_list = [
        "LOGGING_OPTIONS",
        "FFT_OPTIONS",
        "FFT_LIBRARY",
        "MATRIX_MULTIPLICATION",
        "PAUSE_GUI",
    ]
    datachecker.check_dict("data_config", data_config, key_list=key_list)

    # check logging options
    datachecker.check_string("FORMAT", data_config["LOGGING_OPTIONS"]["FORMAT"])
    datachecker.check_string("LEVEL", data_config["LOGGING_OPTIONS"]["LEVEL"])
    datachecker.check_integer("INDENTATION", data_config["LOGGING_OPTIONS"]["INDENTATION"])
    datachecker.check_boolean("EXCEPTION_TRACE", data_config["LOGGING_OPTIONS"]["EXCEPTION_TRACE"])
    datachecker.check_boolean("USE_COLOR", data_config["LOGGING_OPTIONS"]["USE_COLOR"])
    datachecker.check_string("CL_DEBUG", data_config["LOGGING_OPTIONS"]["CL_DEBUG"])
    datachecker.check_string("CL_INFO", data_config["LOGGING_OPTIONS"]["CL_INFO"])
    datachecker.check_string("CL_WARNING", data_config["LOGGING_OPTIONS"]["CL_WARNING"])
    datachecker.check_string("CL_ERROR", data_config["LOGGING_OPTIONS"]["CL_ERROR"])
    datachecker.check_string("CL_CRITICAL", data_config["LOGGING_OPTIONS"]["CL_CRITICAL"])
    datachecker.check_string("CL_RESET", data_config["LOGGING_OPTIONS"]["CL_RESET"])

    # check FFT options
    if data_config["FFT_OPTIONS"]["FFTS_WORKER"] is not None:
        datachecker.check_integer("FFTS_WORKER", data_config["FFT_OPTIONS"]["FFTS_WORKER"])
    if data_config["FFT_OPTIONS"]["FFTW_THREAD"] is not None:
        datachecker.check_integer("FFTW_THREAD", data_config["FFT_OPTIONS"]["FFTW_THREAD"])
    if data_config["FFT_OPTIONS"]["FFTW_BYTE_ALIGN"] is not None:
        datachecker.check_integer("FFTW_BYTE_ALIGN", data_config["FFT_OPTIONS"]["FFTW_BYTE_ALIGN"])
    if data_config["FFT_OPTIONS"]["FFTW_CACHE_TIMEOUT"] is not None:
        datachecker.check_float("FFTW_CACHE_TIMEOUT", data_config["FFT_OPTIONS"]["FFTW_CACHE_TIMEOUT"])

    # check other switches
    datachecker.check_boolean("USE_DOUBLE", data_config["USE_DOUBLE"])
    datachecker.check_float("PAUSE_GUI", data_config["PAUSE_GUI"])
    datachecker.check_choice("FFT_LIBRARY", data_config["FFT_LIBRARY"], ["SciPy", "FFTW", "CuPy"])
    datachecker.check_choice("MATRIX_MULTIPLICATION", data_config["MATRIX_MULTIPLICATION"], ["FFT", "DIRECT"])


def _check_library(data_config):
    """
    Check that the required libraries are installed.
    """

    # check GPU
    if data_config["FFT_LIBRARY"] == "SciPy":
        lib = importlib.util.find_spec("scipy")
        datachecker.check_assert("FFT_LIBRARY", lib is not None, "Library SciPy is not installed")
    elif data_config["FFT_LIBRARY"] == "FFTW":
        lib = importlib.util.find_spec("pyfftw")
        datachecker.check_assert("FFT_LIBRARY", lib is not None, "Library FFTW is not installed")
    elif data_config["FFT_LIBRARY"] == "CuPy":
        lib = importlib.util.find_spec("cupy")
        datachecker.check_assert("FFT_LIBRARY", lib is not None, "Library CuPy is not installed")
    else:
        raise ValueError("invalid FFT library")


def check_data_config(data_config):
    """
    Check and update the config data.
    """

    # check the data integrity
    _check_data(data_config)

    # check that the libraries are installed
    _check_library(data_config)

    # update the configuration
    data_config = _update_data(data_config)

    return data_config
