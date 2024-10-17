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
with importlib.resources.path("pypeec.data", "schema_problem.yaml") as file:
    SCHEMA_PROBLEM = scisave.load_config(file)
with importlib.resources.path("pypeec.data", "schema_tolerance.yaml") as file:
    SCHEMA_TOLERANCE = scisave.load_config(file)
with importlib.resources.path("pypeec.data", "schema_list_viewer.yaml") as file:
    SCHEMA_VIEWER = scisave.load_config(file)
with importlib.resources.path("pypeec.data", "schema_list_plotter.yaml") as file:
    SCHEMA_PLOTTER = scisave.load_config(file)


def check_data_geometry(data_geometry):
    """
    Check the mesher geometry data.
    """

    jsonschema.validate(instance=data_geometry, schema=SCHEMA_GEOMETRY)


def check_data_problem(data_problem):
    """"
    Check the solver problem data.
    """

    jsonschema.validate(instance=data_problem, schema=SCHEMA_PROBLEM)


def check_data_tolerance(data_tolerance):
    """
    Check the solver tolerance data.
    """

    jsonschema.validate(instance=data_tolerance, schema=SCHEMA_TOLERANCE)


def check_data_viewer(data_viewer):
    """
    Check the viewer data.
    """

    jsonschema.validate(instance=data_viewer, schema=SCHEMA_VIEWER)


def check_data_plotter(data_tolerance):
    """
    Check the plotter data.
    """

    jsonschema.validate(instance=data_tolerance, schema=SCHEMA_PLOTTER)
