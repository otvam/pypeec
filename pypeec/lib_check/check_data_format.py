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
import numpy as np
import jsonschema
import scisave

# static data folder
folder = importlib.resources.files("pypeec.data")

# preload the schemas
SCHEMA_GEOMETRY = scisave.load_config(folder.joinpath("schema_geometry.yaml"))
SCHEMA_PROBLEM = scisave.load_config(folder.joinpath("schema_problem.yaml"))
SCHEMA_TOLERANCE = scisave.load_config(folder.joinpath("schema_tolerance.yaml"))
SCHEMA_VIEWER = scisave.load_config(folder.joinpath("schema_list_viewer.yaml"))
SCHEMA_PLOTTER = scisave.load_config(folder.joinpath("schema_list_plotter.yaml"))


def _get_strict_validator():
    """
    Create a strict validator for numerics (integer and floating).
    Cast NumPy arrays as lists for the type check.
    """

    def get_int(_, instance):
        return np.issubdtype(type(instance), np.integer)

    def get_float(_, instance):
        return np.issubdtype(type(instance), np.floating)

    def get_array(_, instance):
        if isinstance(instance, np.ndarray):
            return jsonschema.Draft202012Validator.TYPE_CHECKER.is_type(instance.tolist(), "array")
        else:
            return jsonschema.Draft202012Validator.TYPE_CHECKER.is_type(instance, "array")

    # custom type checker
    type_checker = jsonschema.Draft202012Validator.TYPE_CHECKER
    type_checker = type_checker.redefine("number", get_float)
    type_checker = type_checker.redefine("integer", get_int)
    type_checker = type_checker.redefine("array", get_array)

    # custom validator
    StrictValidator = jsonschema.validators.extend(
        jsonschema.Draft202012Validator,
        type_checker=type_checker,
    )

    return StrictValidator


def _get_validate_schema(data, schema):
    """
    Validate data with strict validator for numerics.
    """

    # get type checker
    StrictValidator = _get_strict_validator()

    # validate schema
    validator = StrictValidator(schema=schema)
    validator.validate(data)


def check_data_geometry(data_geometry):
    """
    Check the mesher geometry data.
    """

    _get_validate_schema(data_geometry, SCHEMA_GEOMETRY)


def check_data_problem(data_problem):
    """
    Check the solver problem data.
    """

    _get_validate_schema(data_problem, SCHEMA_PROBLEM)


def check_data_tolerance(data_tolerance):
    """
    Check the solver tolerance data.
    """

    _get_validate_schema(data_tolerance, SCHEMA_TOLERANCE)


def check_data_viewer(data_viewer):
    """
    Check the viewer data.
    """

    _get_validate_schema(data_viewer, SCHEMA_VIEWER)


def check_data_plotter(data_tolerance):
    """
    Check the plotter data.
    """

    _get_validate_schema(data_tolerance, SCHEMA_PLOTTER)
