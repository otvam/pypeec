"""
Module for the checking the data format:
    - check the user provided options
    - check the data generated by the mesher
    - check the data generated by the solver
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import jsonschema


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
    jsonschema.validate(instance=tag_list, schema=schema)

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
    jsonschema.validate(instance=plot_mode, schema=schema)

    # check folder and name
    schema = {
        "type": ["null", "string"],
        "minLength": 1,
    }
    jsonschema.validate(instance=folder, schema=schema)
    jsonschema.validate(instance=name, schema=schema)


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
    jsonschema.validate(instance=data_voxel, schema=schema)

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
    jsonschema.validate(instance=data_solution, schema=schema)

    # extract fields
    status = data_solution["status"]
    data_init = data_solution["data_init"]
    data_sweep = data_solution["data_sweep"]

    return status, data_init, data_sweep
