"""
Module for transforming a series of 2D vector shapes into a 3D voxel structure.
The 2D geometry are stacked in order to create a voxel structure.

The following axis definition is used:
    - x: x-axis of the 2D shapes
    - y: y-axis of the 2D shapes
    - z: stacking dimension of the 2D geometries

The shape handling is done with Shapely.
The raster conversion is done with Rasterio.

TODO: The warning triggered by Rasterio should be handled in a cleaner way.
      It is not clear which shapes are causing these warnings.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import warnings
import numpy as np
import pyvista as pv
import shapely as sha
import rasterio.features as raf
import rasterio.transform as rat
from pypeec import log
from pypeec import config
from pypeec.error import RunError

# prevent problematic linear transform to trigger warnings
warnings.filterwarnings("ignore", module="rasterio.features")
warnings.filterwarnings("ignore", module="rasterio.transform")

# get a logger
LOGGER = log.get_logger("SHAPE")

# get config
NP_TYPES = config.NP_TYPES


def _get_boundary_polygon(bnd, z_min):
    """
    Convert a Shapely boundary into a PyVista polygon.
    """

    # check that the boundary is closed
    if (not bnd.is_valid) or (not bnd.is_closed):
        raise RunError("invalid shape: boundary is ill-formed")

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
    """
    Extrude a Shapely polygon into a PyVista mesh.
    """

    # ensure that the polygon has a positive orientation
    obj = sha.geometry.polygon.orient(obj)

    # get the exterior boundary and the holes
    bnd = obj.exterior
    holes = obj.interiors

    # polygon for the external boundaries
    polygon = _get_boundary_polygon(bnd, z_min)

    # polygon for the holes
    for bnd in holes:
        polygon += _get_boundary_polygon(bnd, z_min)

    # triangulate the resulting polygon
    polygon = polygon.delaunay_2d(edge_source=polygon)

    # extrude the polygon into a 3D mesh
    mesh = polygon.extrude((0, 0, z_max-z_min), capping=True)

    return mesh


def _get_single_shape(shape_data):
    """
    Get a Shapely object for different shapes:
        - a trace (multi-segment line)
        - a pad (filled disc)
        - a polygon
    """

    # extract the data
    shape_type = shape_data["shape_type"]
    coord = shape_data["coord"]

    # get the shape
    if shape_type == "pad":
        buffer = 0.5*shape_data["diameter"]
        obj = sha.geometry.MultiPoint(coord)
    elif shape_type == "trace":
        buffer = 0.5*shape_data["width"]
        obj = sha.geometry.LineString(coord)
    elif shape_type == "polygon":
        buffer = shape_data["buffer"]
        obj = sha.geometry.Polygon(coord)
    else:
        raise ValueError("invalid shape type")

    # add a buffer with a given thickness around the shape
    if buffer is not None:
        obj = obj.buffer(buffer, cap_style="round", join_style="round")

    # check if valid
    if obj.is_empty:
        raise RunError("invalid shape: shape is empty")

    return obj


def _get_composite_shape(shape_add, shape_sub, tol):
    """
    Get a Shapely composite shape consisting of the union/difference of several shapes.
    Simplify the shape with a given tolerance and check the validity of the shape;
    """

    # shape to be added
    obj_add = []
    for shape_data in shape_add:
        obj_add.append(_get_single_shape(shape_data))

    # shape to be subtracted
    obj_sub = []
    for shape_data in shape_sub:
        obj_sub.append(_get_single_shape(shape_data))

    # form the composite shape
    obj_add = sha.unary_union(obj_add)
    obj_sub = sha.unary_union(obj_sub)
    obj = sha.difference(obj_add, obj_sub)

    # simplify the shape
    obj = sha.simplify(obj, tol)

    # check that the shape is valid
    if not obj.is_valid:
        raise RunError("invalid shape: geometry is ill-formed")

    return obj


def _get_voxelize_shape(n, xyz_min, xyz_max, obj):
    """
    Voxelize a shape with given bounds and voxel numbers.
    """

    # get the bounds for the voxelization
    (nx, ny, nz) = n
    (x_min, y_min, z_min) = xyz_min
    (x_max, y_max, z_max) = xyz_max

    # coordinate transformation for the bounds
    transform = rat.from_bounds(x_min, y_max, x_max, y_min, nx, ny)

    # rasterize the data
    idx_shape = raf.rasterize([obj], out_shape=(ny, nx), transform=transform)

    # get the boolean matrix with the voxelization result
    idx_shape = np.swapaxes(idx_shape, 0, 1)

    # find the 2D indices
    idx_shape = idx_shape.flatten(order="F")
    idx_shape = np.flatnonzero(idx_shape).astype(NP_TYPES.INT)

    return idx_shape


def _get_idx_voxel(n, idx_shape, stack_idx):
    """
    Find the 3D voxel indices from the 2D image indices.
    The number of layers to be added is arbitrary.
    """

    # get the shape size
    (nx, ny, nz) = n

    # init voxel indices
    idx_voxel = np.array([], dtype=NP_TYPES.INT)

    # convert image indices into voxel indices
    for idx in stack_idx:
        # convert indices
        idx_tmp = idx*nx*ny+idx_shape

        # add the indices to the array
        idx_voxel = np.append(idx_voxel, idx_tmp)

    return idx_voxel


def _get_shape_position(layer_start, layer_stop, stack_pos, stack_tag):
    """
    Find the position of a shape in the layer stack.
    Find the absolute position and the indices with respect to the layer stack.
    """

    # find the stack position
    layer_start = np.flatnonzero(stack_tag == layer_start)
    layer_stop = np.flatnonzero(stack_tag == layer_stop)
    layer = np.concatenate((layer_start, layer_stop))

    # find the stack indices
    idx_min = np.min(layer)+0
    idx_max = np.max(layer)+1
    stack_idx = np.arange(idx_min, idx_max)

    # get the position
    z_min = stack_pos[idx_min]
    z_max = stack_pos[idx_max]

    return z_min, z_max, stack_idx


def _get_shape_obj(geometry_shape, stack_pos, stack_tag, tol):
    """
    Create the shapes and set the position in the layer stack.
    Find the bounding box for all the shapes (minimum and maximum coordinates).
    """

    # init shape list
    shape_obj = []

    # init the coordinate (minimum and maximum coordinates)
    xy_min = np.full(2, +np.inf, dtype=NP_TYPES.FLOAT)
    xy_max = np.full(2, -np.inf, dtype=NP_TYPES.FLOAT)

    # create the shapes and find the bounding box
    for tag, geometry_shape_tmp in geometry_shape.items():
        for geometry_shape_tmp_tmp in geometry_shape_tmp:
            # extract the data
            layer_start = geometry_shape_tmp_tmp["layer_start"]
            layer_stop = geometry_shape_tmp_tmp["layer_stop"]
            shape_add = geometry_shape_tmp_tmp["shape_add"]
            shape_sub = geometry_shape_tmp_tmp["shape_sub"]

            # get the shape
            obj = _get_composite_shape(shape_add, shape_sub, tol)

            # get the stack position
            (z_min, z_max, stack_idx) = _get_shape_position(layer_start, layer_stop, stack_pos, stack_tag)

            # find the bounds
            (x_min, y_min, x_max, y_max) = obj.bounds
            tmp_min = np.array((x_min, y_min), dtype=NP_TYPES.FLOAT)
            tmp_max = np.array((x_max, y_max), dtype=NP_TYPES.FLOAT)

            # add the object if not empty
            if not obj.is_empty:
                # update the bounds
                xy_min = np.minimum(xy_min, tmp_min)
                xy_max = np.maximum(xy_max, tmp_max)

                # assign the object
                shape_obj.append({"tag": tag, "z_min": z_min, "z_max": z_max, "stack_idx": stack_idx, "obj": obj})

    return shape_obj, xy_min, xy_max


def _get_layer_stack(layer_stack, dz, cz):
    """
    Parse the layer stack defining with a list.
    Return the number of layers and the coordinates of the layers.
    """

    # init the list
    stack_tag = []

    # get a list with all the layers and the corresponding names
    for layer_stack_tmp in layer_stack:
        n_layer = layer_stack_tmp["n_layer"]
        tag_layer = layer_stack_tmp["tag_layer"]
        stack_tag += n_layer*[tag_layer]

    # get the number of layers
    nz = len(stack_tag)

    # get the z dimension
    z_min = -(nz*dz)/2+cz
    z_max = +(nz*dz)/2+cz

    # get position and name arrays
    stack_pos = np.linspace(z_min, z_max, nz+1)
    stack_tag = np.array(stack_tag)

    return nz, stack_pos, stack_tag


def _get_domain_def(n, d, c, geometry_shape, shape_obj):
    """
    Voxelize the shapes and assign the indices to a dict.
    """

    # get the voxelization bounds
    xyz_min = c-(n*d)/2
    xyz_max = c+(n*d)/2

    # init the domain dict
    domain_def = {}
    for tag in geometry_shape:
        domain_def[tag] = np.array([], NP_TYPES.INT)

    # voxelize the shapes
    for shape_obj_tmp in shape_obj:
        # extract the data
        tag = shape_obj_tmp["tag"]
        obj = shape_obj_tmp["obj"]
        stack_idx = shape_obj_tmp["stack_idx"]

        # voxelize and get the indices
        idx_shape = _get_voxelize_shape(n, xyz_min, xyz_max, obj)
        idx_voxel = _get_idx_voxel(n, idx_shape, stack_idx)

        # append the indices into the corresponding domain
        domain_def[tag] = np.append(domain_def[tag], idx_voxel)

    # remove duplicates
    for tag, idx_voxel in domain_def.items():
        idx_voxel = np.unique(idx_voxel)
        LOGGER.debug("%s: n_voxel = %d" % (tag, len(idx_voxel)))
        domain_def[tag] = idx_voxel

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


def _get_merge_shape(shape_obj):
    """
    Transform all the 2D vector shapes into 3D meshes.
    Merge all the meshes into a single mesh.
    The resulting mesh represent the original geometry.
    This mesh can be used to assess the quality of the voxelization.
    """

    # list for storing the meshes
    mesh_list = []

    # merge all the shapes
    for shape_obj_tmp in shape_obj:
        # extract the data
        obj = shape_obj_tmp["obj"]
        z_min = shape_obj_tmp["z_min"]
        z_max = shape_obj_tmp["z_max"]

        # transform the shapes into meshes
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
    Transform a series of 2D vector shapes into a 3D voxel structure.
    The 3D voxel structure is constructed from:
        - a dict containing the 2D shapes
        - a list containing the layer stack of shapes
    """

    # extract the data
    dx = param["dx"]
    dy = param["dy"]
    dz = param["dz"]
    cz = param["cz"]
    tol = param["tol"]
    xy_min = param["xy_min"]
    xy_max = param["xy_max"]

    # parse layers
    LOGGER.debug("parse the layers")
    (nz, stack_pos, stack_tag) = _get_layer_stack(layer_stack, dz, cz)

    # create the shapes
    LOGGER.debug("create the shapes")
    (shape_obj, xy_min_obj, xy_max_obj) = _get_shape_obj(geometry_shape, stack_pos, stack_tag, tol)

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

    # init domain definition dict
    domain_def = {}
    for tag in geometry_shape:
        domain_def[tag] = np.array([], NP_TYPES.INT)

    # voxelize the shapes and get the indices
    LOGGER.debug("voxelize the shapes")
    domain_def = _get_domain_def(n, d, c, domain_def, shape_obj)

    # merge the shapes representing the original geometry
    LOGGER.debug("merge the shapes")
    reference = _get_merge_shape(shape_obj)

    # cast to lists
    n = n.tolist()
    d = d.tolist()
    c = c.tolist()

    return n, d, c, domain_def, reference
