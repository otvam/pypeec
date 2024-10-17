"""
Module for checking the geometry data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import importlib.resources
import jsonschema
import scisave


def check_data_geometry(data_geometry):
    """
    Check the mesher data type and extract the data.
    """

    # load base schema
    with importlib.resources.path("pypeec.data", "schema_geometry_base.yaml") as file:
        schema = scisave.load_config(file)

    # validate base schema
    jsonschema.validate(instance=data_geometry, schema=schema)

    # extract voxelization data
    mesh_type = data_geometry["mesh_type"]
    data_voxelize = data_geometry["data_voxelize"]

    # load voxelization schema
    if mesh_type == "png":
        with importlib.resources.path("pypeec.data", "schema_geometry_png.yaml") as file:
            schema = scisave.load_config(file)
    elif mesh_type == "stl":
        with importlib.resources.path("pypeec.data", "schema_geometry_stl.yaml") as file:
            schema = scisave.load_config(file)
    elif mesh_type == "shape":
        with importlib.resources.path("pypeec.data", "schema_geometry_shape.yaml") as file:
            schema = scisave.load_config(file)
    elif mesh_type == "voxel":
        with importlib.resources.path("pypeec.data", "schema_geometry_voxel.yaml") as file:
            schema = scisave.load_config(file)
    else:
        raise ValueError("invalid mesh type")

    # validate voxelization schema
    jsonschema.validate(instance=data_voxelize, schema=schema)
