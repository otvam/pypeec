"""
Module for managing the configuration of the program.
The config variables are accessed with attributes.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import sys
import os.path
import pathlib
import importlib.resources
from pypeec import io
from pypeec.lib_check import check_data_config
from pypeec.error import RunError, FileError, CheckError


def __getattr__(name):
    """
    Wrapper to access the config data with attributes.
    """

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

    for tag, data_config_tmp in data_config.items():
        if isinstance(data_config_tmp, dict):
            data_config[tag] = _DictToAttributes(data_config_tmp)
        else:
            data_config[tag] = data_config_tmp

    return data_config


def _set_file_config(file_config):
    """
    Load and set a configuration file.
    This function is be called immediately after initializing the module.
    """

    # load the config file
    try:
        # load the config file
        data_config = io.load_config(file_config)

        # check the data integrity and complete the config
        data_config = check_data_config.check_data_config(data_config)

        # make the dictionary accessible with attributes
        data_config = _parse_config(data_config)

        # assign config to a global variable
        global DATA_CONFIG
        DATA_CONFIG = data_config
    except (FileError, CheckError, RunError) as ex:
        print("==========================")
        print("INVALID CONFIGURATION FILE")
        print("==========================")
        print(str(ex))
        print("==========================")
        sys.exit(1)


# init config data
DATA_CONFIG = dict()

# load the default config files
with importlib.resources.path("pypeec", "config.yaml") as file_config:
    _set_file_config(file_config)

# find the custom files
file_config_list = [
    pathlib.Path.home().joinpath(".pypeec.json"),
    pathlib.Path.home().joinpath(".pypeec.yaml"),
    pathlib.Path.home().joinpath("pypeec.json"),
    pathlib.Path.home().joinpath("pypeec.yaml"),
    pathlib.Path.cwd().joinpath(".pypeec.json"),
    pathlib.Path.cwd().joinpath(".pypeec.yaml"),
    pathlib.Path.cwd().joinpath("pypeec.json"),
    pathlib.Path.cwd().joinpath("pypeec.yaml"),
]

# set the custom files
for file_config in file_config_list:
    if file_config.is_file():
        _set_file_config(file_config)

# check for env variables
file_config = os.getenv("PYPEEC")
if file_config is not None:
    file_config = pathlib.Path(file_config)
    _set_file_config(file_config)
