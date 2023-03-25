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
        "FACTORIZATION_OPTIONS",
        "FACTORIZATION_LIBRARY",
        "MATRIX_SPLIT",
        "MATRIX_MULTIPLICATION",
        "USE_DOUBLE",
        "PAUSE_GUI",
    ]
    datachecker.check_dict("data_config", data_config, key_list=key_list)

    # check logging options
    LOGGING_OPTIONS = data_config["LOGGING_OPTIONS"]
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
    FFT_OPTIONS = data_config["FFT_OPTIONS"]
    if FFT_OPTIONS["FFTS_WORKER"] is not None:
        datachecker.check_integer("FFTS_WORKER", FFT_OPTIONS["FFTS_WORKER"], is_positive=True, can_be_zero=False)
    if FFT_OPTIONS["FFTW_THREAD"] is not None:
        datachecker.check_integer("FFTW_THREAD", FFT_OPTIONS["FFTW_THREAD"], is_positive=True, can_be_zero=False)
    if FFT_OPTIONS["FFTW_BYTE_ALIGN"] is not None:
        datachecker.check_integer("FFTW_BYTE_ALIGN", FFT_OPTIONS["FFTW_BYTE_ALIGN"], is_positive=True)
    if FFT_OPTIONS["FFTW_CACHE_TIMEOUT"] is not None:
        datachecker.check_float("FFTW_CACHE_TIMEOUT", FFT_OPTIONS["FFTW_CACHE_TIMEOUT"], is_positive=True)

    # check factorization options
    FACTORIZATION_OPTIONS = data_config["FACTORIZATION_OPTIONS"]
    datachecker.check_float("ITER_REL_TOL", FACTORIZATION_OPTIONS["ITER_REL_TOL"], is_positive=True, can_be_zero=False)
    datachecker.check_float("ITER_ABS_TOL", FACTORIZATION_OPTIONS["ITER_ABS_TOL"], is_positive=True, can_be_zero=False)
    datachecker.check_integer("ITER_N_MAX", FACTORIZATION_OPTIONS["ITER_N_MAX"], is_positive=True, can_be_zero=False)
    if FACTORIZATION_OPTIONS["THREAD_PARDISO"] is not None:
        datachecker.check_integer("THREAD_PARDISO", FACTORIZATION_OPTIONS["THREAD_PARDISO"], is_positive=True, can_be_zero=False)
    if FACTORIZATION_OPTIONS["THREAD_MKL"] is not None:
        datachecker.check_integer("THREAD_MKL", FACTORIZATION_OPTIONS["THREAD_MKL"], is_positive=True, can_be_zero=False)

    # check other switches
    datachecker.check_boolean("MATRIX_SPLIT", data_config["MATRIX_SPLIT"])
    datachecker.check_boolean("USE_DOUBLE", data_config["USE_DOUBLE"])
    datachecker.check_float("PAUSE_GUI", data_config["PAUSE_GUI"], is_positive=True)
    datachecker.check_choice("MATRIX_MULTIPLICATION", data_config["MATRIX_MULTIPLICATION"], ["FFT", "DIRECT"])

    # check FFT library
    lib = [
        "SciPy",
        "FFTW",
        "CuPy",
    ]
    datachecker.check_choice("FFT_LIBRARY", data_config["FFT_LIBRARY"], lib)

    # check factorization library
    lib =  [
        "SuperLU",
        "UMFPACK",
        "PARDISO",
        "GCROT",
        "BICG",
        "GMRES",
    ]
    datachecker.check_choice("FACTORIZATION_LIBRARY", data_config["FACTORIZATION_LIBRARY"], lib)


def _check_library(data_config):
    """
    Check that the required libraries are installed.
    """

    # check FFT library
    if data_config["FFT_LIBRARY"] == "SciPy":
        lib = importlib.util.find_spec("scipy")
        datachecker.check_assert("FFT_LIBRARY", lib is not None, "SciPy is not installed")
    elif data_config["FFT_LIBRARY"] == "FFTW":
        lib = importlib.util.find_spec("pyfftw")
        datachecker.check_assert("FFT_LIBRARY", lib is not None, "FFTW is not installed")
    elif data_config["FFT_LIBRARY"] == "CuPy":
        lib = importlib.util.find_spec("cupy")
        datachecker.check_assert("FFT_LIBRARY", lib is not None, "CuPy is not installed")
    else:
        raise ValueError("invalid FFT library")

    # check factorization library
    if data_config["FACTORIZATION_LIBRARY"] in ["SuperLU", "GCROT", "BICG", "GMRES"]:
        lib = importlib.util.find_spec("scipy.sparse.linalg")
        datachecker.check_assert("library", lib is not None, "SciPy is not installed")
    elif data_config["FACTORIZATION_LIBRARY"] == "UMFPACK":
        lib = importlib.util.find_spec("scikits.umfpack")
        datachecker.check_assert("library", lib is not None, "UMFPACK is not installed")
    elif data_config["FACTORIZATION_LIBRARY"] == "PARDISO":
        lib = importlib.util.find_spec("pydiso")
        datachecker.check_assert("library", lib is not None, "PARDISO is not installed")
    else:
        raise ValueError("invalid matrix factorization library")


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
