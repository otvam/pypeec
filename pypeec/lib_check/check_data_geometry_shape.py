"""
Module for checking the shape mesher data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

from pypeec.lib_check import datachecker


def _check_shape_data(shape_data):
    """
    Check the validity of a single shape definition.
    """

    # check type
    key_list = ["shape_type", "shape_operation", "coord"]
    datachecker.check_dict("shape", shape_data, key_list=key_list)

    # extract the data
    shape_type = shape_data["shape_type"]
    shape_operation = shape_data["shape_operation"]
    coord = shape_data["coord"]

    # check data
    datachecker.check_choice("shape_operation", shape_operation, ["add", "sub"])
    datachecker.check_choice("shape_type", shape_type, ["trace", "pad", "polygon"])
    datachecker.check_float_pts("coord", coord, size=2, can_be_empty=False)

    # check coordinate length
    if shape_type == "pad":
        datachecker.check_dict("shape", shape_data, key_list=["diameter"])
        datachecker.check_float("diameter", shape_data["diameter"], is_positive=True, can_be_zero=True)
        datachecker.check_assert("coord", len(coord) >= 1, "pad coordinate should have at least one element")
    elif shape_type == "trace":
        datachecker.check_dict("shape", shape_data, key_list=["width"])
        datachecker.check_float("width", shape_data["width"], is_positive=True, can_be_zero=True)
        datachecker.check_assert("coord", len(coord) >= 2, "trace coordinate should have at least two elements")
    elif shape_type == "polygon":
        datachecker.check_dict("shape", shape_data, key_list=["buffer"])
        datachecker.check_float("buffer", shape_data["buffer"], is_positive=True, can_be_zero=True, can_be_none=True)
        datachecker.check_assert("coord", len(coord) >= 3, "polygon coordinate should have at least three elements")
    else:
        raise ValueError("invalid shape type")


def _check_geometry_shape(layer_list, geometry_shape):
    """
    Check the validity of the domain shape definition.
    """

    # check type
    datachecker.check_dict("geometry_shape", geometry_shape, can_be_empty=False)

    # check content
    for tag, geometry_shape_tmp in geometry_shape.items():
        datachecker.check_list("geometry_shape", geometry_shape_tmp, can_be_empty=False)
        for geometry_shape_tmp_tmp in geometry_shape_tmp:
            # check type
            key_list = ["shape_layer", "shape_operation", "shape_data"]
            datachecker.check_dict("geometry_shape", geometry_shape_tmp_tmp, key_list=key_list)

            # extract the data
            shape_layer = geometry_shape_tmp_tmp["shape_layer"]
            shape_operation = geometry_shape_tmp_tmp["shape_operation"]
            shape_data = geometry_shape_tmp_tmp["shape_data"]

            # check data
            datachecker.check_choice("shape_operation", shape_operation, ["add", "sub"])
            datachecker.check_list("shape_layer", shape_layer, can_be_empty=False)
            datachecker.check_list("shape_data", shape_data, can_be_empty=False)

            # check layer
            for shape_layer_tmp in shape_layer:
                datachecker.check_choice("shape_layer", shape_layer_tmp, layer_list)

            # check data
            for shape_data_tmp in shape_data:
                _check_shape_data(shape_data_tmp)


def _check_layer_stack(layer_stack):
    """
    Check the validity of the layer stack definition.
    """

    # list with the layer name
    layer_list = []

    # check type
    datachecker.check_list("layer_stack", layer_stack, can_be_empty=False)

    # check value
    for layer_stack_tmp in layer_stack:
        # check type
        key_list = ["n_layer", "tag_layer"]
        datachecker.check_dict("layer_stack", layer_stack_tmp, key_list=key_list)

        # extract the data
        n_layer = layer_stack_tmp["n_layer"]
        tag_layer = layer_stack_tmp["tag_layer"]

        # check data
        datachecker.check_integer("n_layer", n_layer, is_positive=True, can_be_zero=False)
        datachecker.check_string("tag_layer", tag_layer, can_be_empty=False)

        # add layer name
        layer_list.append(tag_layer)

    return layer_list


def _check_param(param):
    """
    Check the voxel structure parameters.
    """

    # check type
    key_list = ["dx", "dy", "dz", "cz", "tol", "xy_min", "xy_max"]
    datachecker.check_dict("param", param, key_list=key_list)

    # check data
    datachecker.check_float("dx", param["dx"], is_positive=True, can_be_zero=False)
    datachecker.check_float("dy", param["dy"], is_positive=True, can_be_zero=False)
    datachecker.check_float("dz", param["dz"], is_positive=True, can_be_zero=False)
    datachecker.check_float("tol", param["tol"], is_positive=True, can_be_zero=False)
    datachecker.check_float("cz", param["cz"], is_positive=False, can_be_zero=True)
    datachecker.check_float_array("xy_min", param["xy_min"], size=2, is_positive=False, can_be_zero=True, can_be_none=True)
    datachecker.check_float_array("xy_max", param["xy_max"], size=2, is_positive=False, can_be_zero=True, can_be_none=True)


def check_data_voxelize(data_voxelize):
    """
    Check the data used for voxelization.
    """

    # check type
    key_list = ["param", "layer_stack", "geometry_shape"]
    datachecker.check_dict("data_voxelize", data_voxelize, key_list=key_list)

    # extract field
    param = data_voxelize["param"]
    layer_stack = data_voxelize["layer_stack"]
    geometry_shape = data_voxelize["geometry_shape"]

    # check voxel structure parameters
    _check_param(param)

    # check layer stack definition
    layer_list = _check_layer_stack(layer_stack)

    # check the domain shape definition
    _check_geometry_shape(layer_list, geometry_shape)

    # get the domain name
    domain_list = geometry_shape.keys()

    return domain_list
