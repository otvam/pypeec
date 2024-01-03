"""
Module for checking the solver config data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import numpy as np
from pypeec.lib_check import datachecker


def _update_data(data_config):
    """
    Parse and complete the config.
    """

    # get the numerical data types
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
        "PROBLEM_MAX_SIZE",
        "DISPLAY_LOGO",
        "USE_DOUBLE",
        "SWEEP_POOL",
        "PAUSE_GUI",
    ]
    datachecker.check_dict("data_config", data_config, key_list=key_list)

    # check logging options
    LOGGING_OPTIONS = data_config["LOGGING_OPTIONS"]
    key_list = [
        "FORMAT",
        "LEVEL",
        "INDENTATION",
        "EXCEPTION_TRACE",
        "USE_COLOR",
        "DEF_COLOR",
    ]
    datachecker.check_dict("LOGGING_OPTIONS", LOGGING_OPTIONS, key_list=key_list)

    # check logging options content
    datachecker.check_dict("FORMAT", LOGGING_OPTIONS["FORMAT"])
    datachecker.check_string("LEVEL", LOGGING_OPTIONS["LEVEL"], can_be_empty=False)
    datachecker.check_integer("INDENTATION", LOGGING_OPTIONS["INDENTATION"], is_positive=True)
    datachecker.check_boolean("EXCEPTION_TRACE", LOGGING_OPTIONS["EXCEPTION_TRACE"])
    datachecker.check_boolean("USE_COLOR", LOGGING_OPTIONS["USE_COLOR"])
    datachecker.check_dict("DEF_COLOR", LOGGING_OPTIONS["DEF_COLOR"])

    # check logging format definition
    key_list = [
        "LOGGER",
        "TIMESTAMP_FMT",
        "DURATION_FMT",
        "TIMESTAMP_TRC",
        "DURATION_TRC",
    ]
    datachecker.check_dict("FORMAT", LOGGING_OPTIONS["FORMAT"], key_list=key_list)
    datachecker.check_string("LOGGER", LOGGING_OPTIONS["FORMAT"]["LOGGER"], can_be_empty=False)
    datachecker.check_string("TIMESTAMP_FMT", LOGGING_OPTIONS["FORMAT"]["TIMESTAMP_FMT"], can_be_empty=False)
    datachecker.check_string("DURATION_FMT", LOGGING_OPTIONS["FORMAT"]["DURATION_FMT"], can_be_empty=False)
    datachecker.check_integer("TIMESTAMP_TRC", LOGGING_OPTIONS["FORMAT"]["TIMESTAMP_TRC"], is_positive=True)
    datachecker.check_integer("DURATION_TRC", LOGGING_OPTIONS["FORMAT"]["DURATION_TRC"], is_positive=True)

    # check logging color definition
    key_list = [
        "CL_DEBUG",
        "CL_INFO",
        "CL_WARNING",
        "CL_ERROR",
        "CL_CRITICAL",
        "CL_RESET",
    ]
    datachecker.check_dict("DEF_COLOR", LOGGING_OPTIONS["DEF_COLOR"], key_list=key_list)
    datachecker.check_string("CL_DEBUG", LOGGING_OPTIONS["DEF_COLOR"]["CL_DEBUG"], can_be_empty=False)
    datachecker.check_string("CL_INFO", LOGGING_OPTIONS["DEF_COLOR"]["CL_INFO"], can_be_empty=False)
    datachecker.check_string("CL_WARNING", LOGGING_OPTIONS["DEF_COLOR"]["CL_WARNING"], can_be_empty=False)
    datachecker.check_string("CL_ERROR", LOGGING_OPTIONS["DEF_COLOR"]["CL_ERROR"], can_be_empty=False)
    datachecker.check_string("CL_CRITICAL", LOGGING_OPTIONS["DEF_COLOR"]["CL_CRITICAL"], can_be_empty=False)
    datachecker.check_string("CL_RESET", LOGGING_OPTIONS["DEF_COLOR"]["CL_RESET"], can_be_empty=False)

    # check problem size limit
    PROBLEM_MAX_SIZE = data_config["PROBLEM_MAX_SIZE"]
    key_list = [
        "VOXEL_TOTAL",
        "VOXEL_USED",
    ]
    datachecker.check_dict("PROBLEM_MAX_SIZE", PROBLEM_MAX_SIZE, key_list=key_list)
    datachecker.check_integer("VOXEL_TOTAL", PROBLEM_MAX_SIZE["VOXEL_TOTAL"], is_positive=True, can_be_zero=False, can_be_none=True)
    datachecker.check_integer("VOXEL_USED", PROBLEM_MAX_SIZE["VOXEL_USED"], is_positive=True, can_be_zero=False, can_be_none=True)

    # check other switches
    datachecker.check_boolean("DISPLAY_LOGO", data_config["DISPLAY_LOGO"])
    datachecker.check_boolean("USE_DOUBLE", data_config["USE_DOUBLE"])
    datachecker.check_float("PAUSE_GUI", data_config["PAUSE_GUI"], is_positive=True, can_be_zero=True)
    datachecker.check_integer("SWEEP_POOL", data_config["SWEEP_POOL"], is_positive=True, can_be_zero=False, can_be_none=True)


def check_data_config(data_config):
    """
    Check and update the config data.
    """

    # check the data integrity
    _check_data(data_config)

    # update the configuration
    data_config = _update_data(data_config)

    return data_config
