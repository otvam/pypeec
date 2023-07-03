"""
Module for checking the PNG mesher data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

from pypeec.lib_check import datachecker


def _check_domain_color(domain_color):
    """
    Check that the mapping between the pixel colors and the domains is valid.
    """

    # check type
    datachecker.check_dict("domain_color", domain_color, can_be_empty=False)

    # check value
    for color_list in domain_color.values():
        datachecker.check_integer_pts("domain_color", color_list, size=4, can_be_empty=False, is_positive=True, can_be_zero=True)


def _check_layer_stack(layer_stack):
    """
    Check the validity of the image layer stack.
    """

    # check type
    datachecker.check_list("layer_stack", layer_stack, can_be_empty=False)

    # check value
    for layer_stack_tmp in layer_stack:
        # check type
        key_list = ["n_layer", "filename_list"]
        datachecker.check_dict("layer_stack", layer_stack_tmp, key_list=key_list)

        # extract the data
        n_layer = layer_stack_tmp["n_layer"]
        filename_list = layer_stack_tmp["filename_list"]

        # check data
        datachecker.check_integer("n_layer", n_layer, is_positive=True, can_be_zero=False)
        datachecker.check_list("filename_list", filename_list, can_be_empty=False, sub_type=str)

        # check files
        for filename in filename_list:
            datachecker.check_filename("filename_list", filename)


def _check_param(param):
    """
    Check the voxel structure parameters.
    """

    # check type
    key_list = ["d", "c", "size"]
    datachecker.check_dict("param", param, key_list=key_list)

    # check data
    datachecker.check_integer_array("size", param["size"], size=2, is_positive=True, can_be_zero=False)
    datachecker.check_float_array("d", param["d"], size=3, is_positive=True, can_be_zero=False)
    datachecker.check_float_array("c", param["c"], size=3, is_positive=False, can_be_zero=True)


def check_data_voxelize(data_voxelize):
    """
    Check the data used for voxelization.
    """

    # check type
    key_list = ["param", "domain_color", "layer_stack"]
    datachecker.check_dict("data_voxelize", data_voxelize, key_list=key_list)

    # extract field
    param = data_voxelize["param"]
    domain_color = data_voxelize["domain_color"]
    layer_stack = data_voxelize["layer_stack"]

    # check voxel structure parameters
    _check_param(param)

    # check domain colors
    _check_domain_color(domain_color)

    # check the PNG layer stack
    _check_layer_stack(layer_stack)

    # get the domain name
    domain_list = domain_color.keys()

    return domain_list
