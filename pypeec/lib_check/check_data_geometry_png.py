"""
Module for checking the PNG mesher data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

from pypeec.lib_check import datachecker


def _check_domain_color(domain_color):
    """
    Check that the mapping between the pixel colors and the domains is valid (PNG mesher).
    """

    # check type
    datachecker.check_dict("domain_color", domain_color, can_be_empty=False, sub_type=list)

    # check value
    for color_list in domain_color.values():
        # check type
        datachecker.check_list("domain_color", color_list, can_be_empty=False, sub_type=list)

        # check data
        for color in color_list:
            datachecker.check_integer_array("domain_color", color, size=4, is_positive=True)


def _check_layer_stack(layer_stack):
    """
    Check the validity of the image layer stack (PNG mesher).
    """

    # check type
    datachecker.check_list("layer_stack", layer_stack, can_be_empty=False, sub_type=dict)

    # check value
    for layer_stack_tmp in layer_stack:
        # check type
        key_list = ["n_layer", "filename_list"]
        datachecker.check_dict("layer_stack", layer_stack_tmp, key_list=key_list)

        # check data
        datachecker.check_integer("n_layer", layer_stack_tmp["n_layer"], is_positive=True, can_be_zero=False)
        datachecker.check_list("filename_list", layer_stack_tmp["filename_list"], can_be_empty=False, sub_type=str)


def _check_voxel_structure(d, c, size):
    """
    Check the voxel structure parameters.
    """

    datachecker.check_integer_array("size", size, size=2, is_positive=True, can_be_zero=False)
    datachecker.check_float_array("d", d, size=3, is_positive=True, can_be_zero=False)
    datachecker.check_float_array("c", c, size=3)


def check_data_voxelize(data_voxelize):
    """
    Check the data used for voxelization (PNG mesher).
    """

    # check type
    key_list = ["d", "c", "size", "domain_color", "layer_stack"]
    datachecker.check_dict("data_voxelize", data_voxelize, key_list=key_list)

    # extract field
    d = data_voxelize["d"]
    c = data_voxelize["c"]
    size = data_voxelize["size"]
    domain_color = data_voxelize["domain_color"]
    layer_stack = data_voxelize["layer_stack"]

    # check voxel structure parameters
    _check_voxel_structure(d, c, size)

    # check domains and layers
    _check_domain_color(domain_color)
    _check_layer_stack(layer_stack)

    # get the domain name
    domain_name = domain_color.keys()

    return domain_name
