"""
Configuration of the program.
Defined with global variables.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import sys
import importlib.resources
from pypeec.lib_check import check_data_config
from pypeec.lib_utils import fileio
from pypeec.lib_utils.error import FileError, CheckError


def __getattr__(name):
    """
    Wrapper to access the config data with attributes.
    """

    # once loaded, the config cannot be updated
    global CAN_UPDATE
    CAN_UPDATE = False

    return DATA_CONFIG[name]


class _DictToAttributes:
    """
    Wrapper to access dictionary with attributes.
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


def set_config(file_config):
    """
    Load a config file and store the data in global variables.
    """

    # parse the file
    data_config = fileio.load_config(file_config)

    # check the data integrity and complete the config
    data_config = check_data_config.check_data_config(data_config)

    # make the dictionary accessible with attributes
    for tag, dat_tmp in data_config.items():
        if isinstance(dat_tmp, dict):
            data_config[tag] = _DictToAttributes(dat_tmp)

    # assign to global
    if CAN_UPDATE:
        global DATA_CONFIG
        DATA_CONFIG = data_config
    else:
        raise CheckError("config data already used and cannot be updated")


# flag determined if the config can be set
CAN_UPDATE = True

# init config data
DATA_CONFIG = dict()

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
