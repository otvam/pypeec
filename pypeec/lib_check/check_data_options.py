"""
Module for the checking the data format:
    - check the user provided options
    - check the data generated by the mesher
    - check the data generated by the solver
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import scisave


def check_tag_list(data_check, tag_list):
    """
    Check the list of plots to be shown.
    """

    # allowed tags
    tag_allowed = list(data_check.keys())

    # check fields
    schema = {
        "type": ["null", "array"],
        "items": {
            "type": "string",
        },
    }

    # validate base schema
    scisave.validate_schema(tag_list, schema)

    # check tag
    if tag_list is not None:
        for tag in tag_list:
            if tag not in tag_allowed:
                raise ValueError("invalid plot tag: %s" % tag)


def check_plot_options(plot_mode, folder, name):
    """
    Check the plot mode (display or not the plots).
    """

    # check plot_mode
    schema = {
        "type": ["null", "string"],
        "enum": [None, "qt", "nb_int", "nb_std", "save", "debug"],
    }
    scisave.validate_schema(plot_mode, schema)

    # check folder and name
    schema = {
        "type": ["null", "string"],
        "minLength": 1,
    }
    scisave.validate_schema(folder, schema)
    scisave.validate_schema(name, schema)


def check_data_voxel(data_voxel):
    """
    Check the voxel data.
    """

    # check fields
    schema = {
        "type": "object",
        "required": [
            "date",
            "duration",
            "seconds",
            "status",
            "data_geom",
        ],
    }

    # validate base schema
    scisave.validate_schema(data_voxel, schema)

    # extract fields
    status = data_voxel["status"]
    data_geom = data_voxel["data_geom"]

    return status, data_geom


def check_data_solution(data_solution):
    """
    Check the solution data.
    """

    # check fields
    schema = {
        "type": "object",
        "required": [
            "date",
            "duration",
            "seconds",
            "status",
            "data_init",
            "data_sweep",
        ],
    }

    # validate base schema
    scisave.validate_schema(data_solution, schema)

    # extract fields
    status = data_solution["status"]
    data_init = data_solution["data_init"]
    data_sweep = data_solution["data_sweep"]

    return status, data_init, data_sweep
