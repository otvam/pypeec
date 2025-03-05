"""
Module for the checking the data format:
    - check the geometry data (for the mesher)
    - check the problem data (for the solver)
    - check the tolerance data (for the solver)
    - check the viewer data (for the viewer)
    - check the plotter data (for the plotter)

Warning
-------
    - The JSON schemas will detect 99% of the problems.
    - However, the schemas are not fully bulletproof.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import importlib.resources
import scisave

# static data folder
folder = importlib.resources.files("pypeec.data")

# preload the schemas
SCHEMA_GEOMETRY = scisave.load_config(folder.joinpath("schema_geometry.yaml"))
SCHEMA_PROBLEM = scisave.load_config(folder.joinpath("schema_problem.yaml"))
SCHEMA_TOLERANCE = scisave.load_config(folder.joinpath("schema_tolerance.yaml"))
SCHEMA_VIEWER = scisave.load_config(folder.joinpath("schema_list_viewer.yaml"))
SCHEMA_PLOTTER = scisave.load_config(folder.joinpath("schema_list_plotter.yaml"))


def check_data_geometry(data_geometry):
    """
    Check the mesher geometry data.
    """

    scisave.validate_schema(data_geometry, SCHEMA_GEOMETRY)


def check_data_problem(data_problem):
    """
    Check the solver problem data.
    """

    scisave.validate_schema(data_problem, SCHEMA_PROBLEM)


def check_data_tolerance(data_tolerance):
    """
    Check the solver tolerance data.
    """

    scisave.validate_schema(data_tolerance, SCHEMA_TOLERANCE)


def check_data_viewer(data_viewer):
    """
    Check the viewer data.
    """

    scisave.validate_schema(data_viewer, SCHEMA_VIEWER)


def check_data_plotter(data_tolerance):
    """
    Check the plotter data.
    """

    scisave.validate_schema(data_tolerance, SCHEMA_PLOTTER)
