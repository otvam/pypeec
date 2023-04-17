"""
Module for transforming a series of 2D shapes into a 3D voxel structure.

The following axis definition is used:
    - x: x-axis of the 2D shapes
    - y: y-axis of the 2D shapes
    - z: stacking dimension of the 2D geometries

The shape handling is done with Shapely.
The rasterization is done with Rasterio.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import numpy as np
import shapely as sha
import rasterio.features as raf
import rasterio.transform as rat
from pypeec import utils_log
from pypeec import config
from pypeec.error import RunError

# get a logger
LOGGER = utils_log.get_logger("SHAPE")

# get config
NP_TYPES = config.NP_TYPES


def _get_single_shape(shape_data):
    shape_type = shape_data["shape_type"]
    buffer = shape_data["buffer"]
    coord = shape_data["coord"]

    if shape_type == "trace":
        obj_tmp = sha.geometry.LineString(coord)
    elif shape_type == "pad":
        obj_tmp = sha.geometry.MultiPoint(coord)
    elif shape_type == "polygon":
        obj_tmp = sha.geometry.Polygon(coord)
    else:
        raise ValueError("invalid shape type")

    obj_final = obj_tmp.buffer(buffer, cap_style=1)

    return obj_final


def _get_composite_shape(shape_add, shape_sub, tol):
    obj_add = []
    for shape_data in shape_add:
        obj_add.append(_get_single_shape(shape_data))

    obj_sub = []
    for shape_data in shape_sub:
        obj_sub.append(_get_single_shape(shape_data))

    obj_add = sha.unary_union(obj_add)
    obj_sub = sha.unary_union(obj_sub)
    obj = sha.difference(obj_add, obj_sub)
    obj = sha.simplify(obj, tol)

    return obj


def _get_shape_position(layer_start, layer_stop, stack_pos, stack_name):
    # find the stack position
    layer_start = np.flatnonzero(stack_name == layer_start)
    layer_stop = np.flatnonzero(stack_name == layer_stop)
    layer = np.concatenate((layer_start, layer_stop))

    # find the stack indices
    idx_min = np.min(layer)
    idx_max = np.max(layer)

    # get the position
    z_min = stack_pos[idx_min+0]
    z_max = stack_pos[idx_max+1]

    return z_min, z_max


def _get_shape_obj(geometry_shape, stack_pos, stack_name, tol):
    # init STL mesh dict
    shape_obj = {}

    # init the coordinate (minimum and maximum coordinates)
    xy_min = np.full(2, +np.inf, dtype=NP_TYPES.FLOAT)
    xy_max = np.full(2, -np.inf, dtype=NP_TYPES.FLOAT)

    # load the STL files and find the bounding box
    for tag, dat_tmp in geometry_shape.items():
        # extract data
        layer_start = dat_tmp["layer_start"]
        layer_stop = dat_tmp["layer_stop"]
        shape_add = dat_tmp["shape_add"]
        shape_sub = dat_tmp["shape_sub"]

        # get the shape
        obj = _get_composite_shape(shape_add, shape_sub, tol)

        # display the shape size
        LOGGER.debug("%s: n_add = %d / n_sub = %d" % (tag, len(shape_add), len(shape_add)))

        # find the bounds
        (x_min, y_min, x_max, y_max) = obj.bounds
        tmp_min = np.array((x_min, y_min), dtype=NP_TYPES.FLOAT)
        tmp_max = np.array((x_max, y_max), dtype=NP_TYPES.FLOAT)

        # update the bounds
        xy_min = np.minimum(xy_min, tmp_min)
        xy_max = np.maximum(xy_max, tmp_max)

        # get the stack position
        (z_min, z_max) = _get_shape_position(layer_start, layer_stop, stack_pos, stack_name)

        # assign the object
        shape_obj[tag] = {"z_min": z_min, "z_max": z_max, "obj": obj}

    return shape_obj, xy_min, xy_max


def _get_layer_stack(layer_stack, dz, cz):
    # init the list
    stack_name = []

    # get the layer parameters
    for dat_tmp in layer_stack:
        n_layer = dat_tmp["n_layer"]
        name_layer = dat_tmp["name_layer"]
        stack_name += n_layer*[name_layer]

    # get the number of layers
    nz = len(stack_name)

    # get the z dimension
    z_min = -(nz*dz)/2+cz
    z_max = +(nz*dz)/2+cz

    # get position and name arrays
    stack_pos = np.linspace(z_min, z_max, nz+1)
    stack_name = np.array(stack_name)

    return nz, stack_pos, stack_name


def _get_voxel_size(dx, dy, dz, stack_pos, xy_max, xy_min):
    """
    Get the parameters (size, dimension, and center) of the voxel structure.
    """

    # get the voxel geometry
    (x_min, y_min) = xy_min
    (x_max, y_max) = xy_max

    # get the z dimension
    z_min = np.min(stack_pos)
    z_max = np.max(stack_pos)

    # get the arrays
    d = np.array([dx, dy, dz], dtype=NP_TYPES.FLOAT)
    xyz_min = np.array([x_min, y_min, z_min], dtype=NP_TYPES.FLOAT)
    xyz_max = np.array([x_max, y_max, z_max], dtype=NP_TYPES.FLOAT)

    # geometry size
    c = (xyz_max+xyz_min)/2

    # extract the number of voxels and the voxel size
    n = np.rint((xyz_max-xyz_min)/d)
    d = (xyz_max-xyz_min)/n

    # cast data
    d = d.astype(NP_TYPES.FLOAT)
    n = n.astype(NP_TYPES.INT)

    # disp geometry size
    LOGGER.debug("voxel: min = (x, y, z) =  (%.3e, %.3e, %.3e)" % tuple(xyz_min))
    LOGGER.debug("voxel: max = (x, y, z) =  (%.3e, %.3e, %.3e)" % tuple(xyz_max))
    LOGGER.debug("voxel: center = (x, y, z) =  (%.3e, %.3e, %.3e)" % tuple(c))

    # check voxel validity
    if not np.all(d > 0):
        RunError("invalid voxel dimension: should be positive")
    # check voxel validity
    if not np.all(n > 0):
        RunError("invalid voxel number: should be positive")

    return n, d, c


def get_mesh(param, layer_stack, geometry_shape):
    """
    Transform a series of 2D shapes into a 3D voxel structure.
    The 3D voxel structure is constructed from:
        - a dict containing the 2D shapes
        - a list containing the layer stack of shapes
    """

    # extract data
    dx = param["dx"]
    dy = param["dy"]
    dz = param["dz"]
    cz = param["cz"]
    tol = param["tol"]
    xy_min = param["xy_min"]
    xy_max = param["xy_max"]

    # parse layers
    LOGGER.debug("parse the layers")
    (nz, stack_pos, stack_name) = _get_layer_stack(layer_stack, dz, cz)

    # create the shapes
    LOGGER.debug("create the shapes")
    (shape_obj, xy_min_obj, xy_max_obj) = _get_shape_obj(geometry_shape, stack_pos, stack_name, tol)

    # if provided, the user specified bounds are used, otherwise the STL bounds
    if xy_min is not None:
        xy_min = np.array(xy_min, NP_TYPES.FLOAT)
    else:
        xy_min = xy_min_obj
    if xy_max is not None:
        xy_max = np.array(xy_max, NP_TYPES.FLOAT)
    else:
        xy_max = xy_max_obj

    # geometry size
    LOGGER.debug("get the voxel size")
    (n, d, c) = _get_voxel_size(dx, dy, dz, stack_pos, xy_max, xy_min)




    # cast to lists
    n = n.tolist()
    d = d.tolist()
    c = c.tolist()

    return n, d, c, domain_def
