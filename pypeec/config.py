"""
Module managing the configuration of the program.
    - The config variables are accessed with attributes.
    - First the default configuration is loaded ("pypeec/data/config.yaml").
    - Afterward, a custom file can be loaded via the environment variable ("PYPEEC").

Warning
-------
    - The configuration is loaded by different PyPEEC modules.
    - The configuration cannot be updated after the initialization.
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

    if name in DATA_CONFIG:
        return DATA_CONFIG[name]
    else:
        return None


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

        # assign config to a global variable
        global FILE_CONFIG
        FILE_CONFIG = str(file_config)
    except (FileError, CheckError, RunError) as ex:
        print("==========================", file=sys.stderr)
        print("INVALID CONFIGURATION FILE", file=sys.stderr)
        print("==========================", file=sys.stderr)
        print(str(ex), file=sys.stderr)
        print("==========================", file=sys.stderr)
        sys.exit(1)


def get_file_config():
    """
    Return the loaded configuration file.

    Returns
    -------
    file_config : string
        String with the loaded configuration file.
    """

    global FILE_CONFIG

    return FILE_CONFIG


def get_data_config():
    """
    Return the loaded configuration data.

    Returns
    -------
    data_config : dict
        Dict with the loaded configuration data.
    """

    global DATA_CONFIG

    return DATA_CONFIG


def get_version():
    """
    Get the PyPEEC version.

    Returns
    -------
    version : string
        String with the PyPEEC version.
    """

    try:
        with importlib.resources.open_text("pypeec.data", "version.txt") as file_version:
            version = file_version.read()
    except FileNotFoundError:
        version = 'x.x.x'

    return version


# init config data
DATA_CONFIG = dict()
FILE_CONFIG = None

# load the default config files
with importlib.resources.path("pypeec.data", "config.yaml") as file_config:
    _set_file_config(file_config)

# check for env variables
file_config = os.getenv("PYPEEC")
if file_config is not None:
    file_config = pathlib.Path(file_config)
    _set_file_config(file_config)
