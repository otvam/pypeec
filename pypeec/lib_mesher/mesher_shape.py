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
import pyvista as pv
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

    if (not obj.is_valid) or (not obj.is_simple):
        raise RunError("invalid polygon: polygon is ill-formed")

    return obj


def _get_shape_position(layer_start, layer_stop, stack_pos, stack_name):
    # find the stack position
    layer_start = np.flatnonzero(stack_name == layer_start)
    layer_stop = np.flatnonzero(stack_name == layer_stop)
    layer = np.concatenate((layer_start, layer_stop))

    # find the stack indices
    idx_min = np.min(layer)+0
    idx_max = np.max(layer)+1
    stack_idx = np.arange(idx_min, idx_max)

    # get the position
    z_min = stack_pos[idx_min]
    z_max = stack_pos[idx_max]

    return z_min, z_max, stack_idx


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
        (z_min, z_max, stack_idx) = _get_shape_position(layer_start, layer_stop, stack_pos, stack_name)

        # assign the object
        shape_obj[tag] = {"z_min": z_min, "z_max": z_max, "stack_idx": stack_idx, "obj": obj}

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


def _get_voxelize_shape(n, xyz_min, xyz_max, obj, stack_idx):
    # get the bounds for the voxelization
    (nx, ny, nz) = n
    (x_min, y_min, z_min) = xyz_min
    (x_max, y_max, z_max) = xyz_max

    # coordinate transformation for the bounds
    transform = rat.from_bounds(x_min, y_min, x_max, y_max, nx, ny)

    # rasterize the data
    matrix = raf.rasterize([obj], out_shape=(ny, nx), transform=transform)

    # get the boolean matrix with the voxelization result
    matrix = np.flip(matrix, axis=1)
    matrix = np.swapaxes(matrix, 0, 1)

    # find the 2D indices
    idx_matrix = matrix.flatten(order="F")
    idx_matrix = np.flatnonzero(idx_matrix).astype(NP_TYPES.INT)

    # init voxel indices
    idx_voxel = np.array([], dtype=NP_TYPES.INT)

    # convert image indices into voxel indices
    for idx in stack_idx:
        # convert indices
        idx_tmp = idx*nx*ny+idx_matrix

        # add the indices to the array
        idx_voxel = np.append(idx_voxel, idx_tmp)

    return idx_voxel


def _get_idx_shape(n, d, c, shape_obj):
    # get the voxelization bounds
    xyz_min = c-(n*d)/2
    xyz_max = c+(n*d)/2

    # init the domain dict
    domain_def = {}

    # load the STL files
    for tag, dat_tmp in shape_obj.items():
        # get the data
        obj = dat_tmp["obj"]
        stack_idx = dat_tmp["stack_idx"]

        # voxelize and get the indices
        idx = _get_voxelize_shape(n, xyz_min, xyz_max, obj, stack_idx)

        # display number of voxels
        LOGGER.debug("%s: n_voxel = %d" % (tag, len(idx)))

        # assign the indices to the domain
        domain_def[tag] = idx

    return domain_def


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


def _get_boundary_polygon(bnd, z_min):
    # check that the boundary is closed
    if (not bnd.is_valid) or (not bnd.is_closed):
        raise RunError("invalid polygon: boundary is ill-formed")

    # get the 2D boundary
    xy = np.array(bnd.xy, dtype=NP_TYPES.FLOAT)
    xy = np.swapaxes(xy, 0, 1)

    # get the 3D boundary
    z = np.full(len(xy), z_min, dtype=NP_TYPES.FLOAT)
    z = np.expand_dims(z, axis=1)
    xyz = np.hstack((xy, z))

    # remove the duplicated points
    xyz = xyz[:-1]

    # get the face indices
    faces = np.arange(len(xyz)+1)
    faces = np.roll(faces, 1)

    # create the polygon
    polygon = pv.PolyData(xyz, faces=faces)

    return polygon


def _get_shape_mesh(z_min, z_max, obj):
    obj = sha.geometry.polygon.orient(obj)

    # bounding polygon
    bnd = obj.exterior
    polygon = _get_boundary_polygon(bnd, z_min)

    # add all holes
    for bnd in obj.interiors:
        polygon += _get_boundary_polygon(bnd, z_min)

    # triangulate poly with all three subpolygons supplying edges
    polygon = polygon.delaunay_2d(edge_source=polygon)

    # extrude
    mesh = polygon.extrude((0, 0, z_max-z_min), capping=True)

    return mesh


def _get_merge_shape(shape_obj):
    # list for storing the meshes
    mesh_list = []

    # load the STL files
    for dat_tmp in shape_obj.values():
        # get the data
        obj = dat_tmp["obj"]
        z_min = dat_tmp["z_min"]
        z_max = dat_tmp["z_max"]

        if isinstance(obj, sha.Polygon):
            mesh = _get_shape_mesh(z_min, z_max, obj)
            mesh_list.append(mesh)
        elif isinstance(obj, sha.MultiPolygon):
            for obj_tmp in obj.geoms:
                mesh = _get_shape_mesh(z_min, z_max, obj_tmp)
                mesh_list.append(mesh)
        else:
            raise ValueError("invalid shape type")

    # assemble the meshes
    reference = pv.MultiBlock(mesh_list)
    reference = reference.combine().extract_surface()

    return reference


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

    # voxelize the meshes and get the indices
    LOGGER.debug("voxelize the shapes")
    domain_def = _get_idx_shape(n, d, c, shape_obj)

    # merge the meshes representing the original geometry
    LOGGER.debug("merge the meshes")
    reference = _get_merge_shape(shape_obj)

    # cast to lists
    n = n.tolist()
    d = d.tolist()
    c = c.tolist()

    return n, d, c, domain_def, reference
