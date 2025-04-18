"""
Module for the checking the user provided options.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import scisave


def check_tag_list(data_check, tag_list):
    """
    Check the list of plots to be shown.
    """

    # check tag_list with a schema
    schema = {
        "type": ["null", "array"],
        "items": {
            "type": "string",
            "minLength": 1,
        },
    }
    scisave.validate_schema(tag_list, schema)

    # get a list with the allowed tags
    tag_allowed = list(data_check.keys())

    # check that the provided tags a subset of the allowed tags
    if tag_list is not None:
        for tag in tag_list:
            if tag not in tag_allowed:
                raise ValueError("invalid plot tag: %s", tag)


def check_plot_options(plot_mode, path, name):
    """
    Check the plot mode (display or not the plots).
    """

    # check plot_mode with a schema
    schema = {
        "type": ["null", "string"],
        "enum": [None, "qt", "nb_int", "nb_std", "png", "vtk", "debug"],
    }
    scisave.validate_schema(plot_mode, schema)

    # check path and name with a schema
    schema = {
        "type": ["null", "string"],
        "minLength": 1,
    }
    scisave.validate_schema(path, schema)
    scisave.validate_schema(name, schema)
