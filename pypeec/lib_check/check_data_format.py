"""
Module for the checking the data formats.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import importlib.resources
import jsonschema
import scisave


# preload the schemas
with importlib.resources.path("pypeec.data", "schema_geometry.yaml") as file:
    SCHEMA_GEOMETRY = scisave.load_config(file)


def check_data_geometry(data_geometry):
    """
    Check the mesher data type and extract the data.
    """

    jsonschema.validate(instance=data_geometry, schema=SCHEMA_GEOMETRY)

