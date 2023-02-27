"""
Module for checking the mesher data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

from PyPEEC.lib_utils import datachecker


def _check_voxel_domain_def(domain_def):
    """
    Check the domain definition (mapping between domain names and indices).
    """

    # check type
    datachecker.check_dict("domain_def", domain_def, can_be_empty=False, sub_type=list)

    # check data
    for idx in domain_def.values():
        datachecker.check_integer_array("domain_def", idx, is_positive=True, can_be_empty=False)


def _check_voxel_indices(n, domain_def):
    """
    Get the validity of the indices.
    """

    # get the indices
    idx_all = []
    for idx in domain_def.values():
        idx_all += idx

    # extract the voxel data
    (nx, ny, nz) = n
    nv = nx*ny*nz

    # check the indices
    datachecker.check_index_array("domain_def", idx_all, bnd=nv, can_be_empty=False)


def _check_png_domain_color(domain_color):
    """
    Check that the mapping between the pixel colors and the domains is valid (PNG mesher).
    """

    # check type
    datachecker.check_dict("domain_color", domain_color, can_be_empty=False, sub_type=list)

    # check value
    for color in domain_color.values():
        datachecker.check_integer_array("domain_color", color, size=4, is_positive=True)


def _check_png_layer_stack(layer_stack):
    """
    Check the validity of the image layer stack (PNG mesher).
    """

    # check type
    datachecker.check_list("layer_stack", layer_stack, can_be_empty=False, sub_type=dict)

    # check value
    for layer_stack_tmp in layer_stack:
        # check type
        key_list = ["n_layer", "filename"]
        datachecker.check_dict("layer_stack", layer_stack_tmp, key_list=key_list)

        # get the data
        n_layer = layer_stack_tmp["n_layer"]
        filename = layer_stack_tmp["filename"]

        # check data
        datachecker.check_integer("n_layer", n_layer, is_positive=True, can_be_zero=False)
        datachecker.check_string("filename", filename)


def _check_stl_domain_stl(domain_stl):
    """
    Check the validity of the domain definition (STL mesher).
    """

    # check type
    datachecker.check_dict("domain_stl", domain_stl, can_be_empty=False, sub_type=str)


def _check_stl_domain_conflict(domain_conflict):
    """
    Check the validity of the rules to solve conflict between domains (STL mesher).
    """

    # check type
    datachecker.check_list("domain_conflict", domain_conflict, sub_type=dict)

    # check value
    for domain_conflict_tmp in domain_conflict:
        # check type
        key_list = ["domain_keep", "domain_resolve"]
        datachecker.check_dict("domain_conflict", domain_conflict_tmp, key_list=key_list)

        # extract data
        domain_keep = domain_conflict_tmp["domain_keep"]
        domain_resolve = domain_conflict_tmp["domain_resolve"]

        # check type
        datachecker.check_string("domain_keep", domain_keep)
        datachecker.check_string("domain_resolve", domain_resolve)


def _check_stl_name(domain_conflict, domain_name):
    """
    Check the consistency of the domain names.
    """

    for domain_conflict_tmp in domain_conflict:
        # extract data
        domain_resolve = domain_conflict_tmp["domain_resolve"]
        domain_keep = domain_conflict_tmp["domain_keep"]

        # check data
        datachecker.check_choice("domain_resolve", domain_resolve, domain_name)
        datachecker.check_choice("domain_keep", domain_keep, domain_name)


def _check_data_voxelize_png(data_voxelize):
    """
    Check the data used for voxelization (PNG mesher).
    """

    # check type
    key_list = ["d", "c", "nx", "ny", "domain_color", "layer_stack"]
    datachecker.check_dict("data_voxelize", data_voxelize, key_list=key_list)

    # extract field
    d = data_voxelize["d"]
    c = data_voxelize["c"]
    nx = data_voxelize["nx"]
    ny = data_voxelize["ny"]
    domain_color = data_voxelize["domain_color"]
    layer_stack = data_voxelize["layer_stack"]

    # check data
    datachecker.check_float_array("d", d, size=3, is_positive=True, can_be_zero=False)
    datachecker.check_float_array("c", c, size=3)
    datachecker.check_integer("nx", nx, is_positive=True, can_be_zero=False)
    datachecker.check_integer("ny", ny, is_positive=True, can_be_zero=False)

    # check domains and layers
    _check_png_domain_color(domain_color)
    _check_png_layer_stack(layer_stack)

    # get the domain name
    domain_name = domain_color.keys()

    return domain_name


def _check_data_voxelize_stl(data_voxelize):
    """
    Check the data used for voxelization (STL mesher).
    """

    # check type
    key_list = ["n", "d", "c", "sampling", "pts_min", "pts_max", "domain_stl", "domain_conflict"]
    datachecker.check_dict("data_voxelize", data_voxelize, key_list=key_list)

    # extract field
    n = data_voxelize["n"]
    d = data_voxelize["d"]
    c = data_voxelize["c"]
    sampling = data_voxelize["sampling"]
    pts_min = data_voxelize["pts_min"]
    pts_max = data_voxelize["pts_max"]
    domain_stl = data_voxelize["domain_stl"]
    domain_conflict = data_voxelize["domain_conflict"]

    # check data
    datachecker.check_choice("sampling", sampling, ["number", "dimension"])
    if sampling == "number":
        datachecker.check_integer_array("n", n, size=3, is_positive=True, can_be_zero=False)
    elif sampling == "dimension":
        datachecker.check_float_array("d", d, size=3, is_positive=True, can_be_zero=False)
    else:
        raise ValueError("inconsistent definition of the voxel number/size")

    # check data
    if c is not None:
        datachecker.check_float_array("c", c, size=3)
    if pts_min is not None:
        datachecker.check_float_array("pts_min", pts_min, size=3)
    if pts_max is not None:
        datachecker.check_float_array("pts_max", pts_max, size=3)

    # check the stl file
    _check_stl_domain_stl(domain_stl)
    _check_stl_domain_conflict(domain_conflict)

    # get the domain name
    domain_name = domain_stl.keys()

    # check domain name
    _check_stl_name(domain_conflict, domain_name)

    return domain_name


def _check_data_voxelize_voxel(data_voxelize):
    """
    Check the voxel structure (number, placement, and dimension).
    Check the mapping between domain names and indices.
    """

    # check type
    key_list = ["n", "d", "c", "domain_def"]
    datachecker.check_dict("data_voxelize", data_voxelize, key_list=key_list)

    # extract field
    n = data_voxelize["n"]
    d = data_voxelize["d"]
    c = data_voxelize["c"]
    domain_def = data_voxelize["domain_def"]

    # check data
    datachecker.check_integer_array("n", n, size=3, is_positive=True, can_be_zero=False)
    datachecker.check_float_array("d", d, size=3, is_positive=True, can_be_zero=False)
    datachecker.check_float_array("c", c, size=3)

    # check domain definition
    _check_voxel_domain_def(domain_def)

    # get the domain name
    domain_name = domain_def.keys()

    # check indices range
    _check_voxel_indices(n, domain_def)

    return domain_name


def _check_domain_connection(domain_connection, domain_name):
    """
    Check the domain connection data.
    This list is defining the required connection between the domain
    """

    # check type
    datachecker.check_dict("domain_connection", domain_connection, sub_type=dict)

    # check value
    for dat_tmp in domain_connection.values():
        # check type
        key_list = ["connected", "domain_list"]
        datachecker.check_dict("domain_connection", dat_tmp, key_list=key_list)

        # extract field
        domain_list = dat_tmp["domain_list"]
        connected = dat_tmp["connected"]

        # check data
        datachecker.check_boolean("connected", connected)
        datachecker.check_list("domain_list", domain_list, can_be_empty=False, sub_type=str)

        # check value
        for tag in domain_list:
            datachecker.check_choice("source_type", tag, domain_name)


def get_domain_stl_path(domain_stl, path_ref):
    """
    Update the filename of the STL files with respect to the provided path.
    """

    # if None, the specified path are already correct
    if path_ref is None:
        return domain_stl

    # check the path
    datachecker.check_string("path_ref", path_ref)

    # init new domain description
    domain_stl_path = {}

    # check value
    for tag, filename in domain_stl.items():
        # check file
        filename = path_ref + "/" + filename
        datachecker.check_filename("filename", filename)

        # add the new item
        domain_stl_path[tag] = filename

    return domain_stl_path


def get_layer_stack_path(layer_stack, path_ref):
    """
    Update the filename of the PNG images with respect to the provided path.
    """

    # if None, the specified path are already correct
    if path_ref is None:
        return layer_stack

    # check the path
    datachecker.check_string("path_ref", path_ref)

    # init new layer stack
    layer_stack_path = []

    # update value
    for layer_stack_tmp in layer_stack:
        # get the data
        n_layer = layer_stack_tmp["n_layer"]
        filename = layer_stack_tmp["filename"]

        # check file
        filename = path_ref + "/" + filename
        datachecker.check_filename("filename", filename)

        # add the new item
        layer_stack_path.append({"n_layer": n_layer, "filename": filename})

    return layer_stack_path


def check_data_mesher(data_mesher):
    """
    Check the mesher data type and extract the data.
    """

    # check type
    key_list = ["mesh_type",
        "data_voxelize",
        "resampling_factor",
        "domain_connection",
    ]
    datachecker.check_dict("data_mesher", data_mesher, key_list=key_list)

    # extract field
    mesh_type = data_mesher["mesh_type"]
    data_voxelize = data_mesher["data_voxelize"]
    resampling_factor = data_mesher["resampling_factor"]
    domain_connection = data_mesher["domain_connection"]

    # check type
    datachecker.check_choice("mesh_type", mesh_type, ["stl", "png", "voxel"])

    # check the mesher
    if mesh_type == "png":
        domain_name = _check_data_voxelize_png(data_voxelize)
    elif mesh_type == "stl":
        domain_name = _check_data_voxelize_stl(data_voxelize)
    elif mesh_type == "voxel":
        domain_name = _check_data_voxelize_voxel(data_voxelize)
    else:
        raise ValueError("invalid mesh type")

    # check the resampling data
    datachecker.check_integer_array("resampling_factor", resampling_factor, size=3, is_positive=True, can_be_zero=False)

    # check the connection data
    _check_domain_connection(domain_connection, domain_name)
