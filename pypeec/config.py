"""
Module for managing the configuration of the program.
The config variables are accessed with attributes.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import sys
import importlib.resources
from pypeec.lib_utils import fileio
from pypeec.lib_check import check_data_config
from pypeec.error import RunError, FileError, CheckError


def __getattr__(name):
    """
    Wrapper to access the config data with attributes.
    """

    # once used, the config cannot be updated
    global CAN_UPDATE
    CAN_UPDATE = False

    return DATA_CONFIG[name]


class _DictToAttributes:
    """
    Wrapper to access a dictionary with attributes.
    """

    def __init__(self, data):
        """
        Set a dictionary.
        """

        self.data = data

    def __getattr__(self, name):
        """
        Access the dictionary with attributes.
        """

        return self.data[name]


def _parse_config(data_config):
    """
    Make the config accessible with attributes.
    """

    for tag, dat_tmp in data_config.items():
        if isinstance(dat_tmp, dict):
            data_config[tag] = _DictToAttributes(dat_tmp)

    return data_config


def _assign_config(data_config):
    """
    Assign the config (if possible).
    """

    if CAN_UPDATE:
        global DATA_CONFIG
        DATA_CONFIG = data_config
    else:
        raise RunError("config data already used and cannot be updated")


def set_config(file_config):
    """
    Load and set a configuration file.
    This function should be called immediately after initializing the module.

    Parameters
    ----------
    file_config : string (input file, JSON or YAML format)

    Returns
    -------
    status : boolean
        True if the call is successful.
        False if the problems are encountered.
    """

    try:
        # parse the file
        data_config = fileio.load_config(file_config)

        # check the data integrity and complete the config
        data_config = check_data_config.check_data_config(data_config)

        # make the dictionary accessible with attributes
        data_config = _parse_config(data_config)

        # assign config to a global variable
        _assign_config(data_config)
    except (FileError, CheckError, RunError) as ex:
        print("==========================")
        print("INVALID CONFIGURATION FILE")
        print("==========================")
        print(str(ex))
        print("==========================")
        return False

    return True


# flag determined if the config can be set
CAN_UPDATE = True

# init config data
DATA_CONFIG = dict()

# load the default config files
with importlib.resources.path("pypeec", "pypeec.yaml") as default_file_config:
    status = set_config(default_file_config)
    if not status:
        sys.exit(1)
