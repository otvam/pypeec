"""
Module for transforming a series of 2D vector shapes into a 3D voxel structure.
The 2D geometry are stacked in order to create a voxel structure.

The following axis definition is used:
    - x: x-axis of the 2D shapes
    - y: y-axis of the 2D shapes
    - z: stacking dimension of the 2D geometries

The shape handling is done with Shapely.
The raster conversion is done with Rasterio.

Todo
----
- The warning triggered by Shapely and Rasterio should be handled in a cleaner way.
    - Rasterio triggers warnings for some coordinate transformations.
    - Shapely triggers warnings on Apple Silicon CPUs.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import warnings
import scilogger
import numpy as np
import pyvista as pv
import shapely as sha
import rasterio.features as raf
import rasterio.transform as rat

# prevent problematic linear transform to trigger warnings
warnings.filterwarnings("ignore", module="shapely")
warnings.filterwarnings("ignore", module="rasterio.features")
warnings.filterwarnings("ignore", module="rasterio.transform")

# get a logger
LOGGER = scilogger.get_logger(__name__, "pypeec")


def _get_boundary_polygon(bnd, z_min):
    """
    Convert a Shapely boundary into a PyVista polygon.
    """

    # check that the boundary is closed
    if (not bnd.is_valid) or (not bnd.is_closed):
        raise RuntimeError("invalid shape: boundary is ill-formed")

    # get the 2D boundary
    xy = np.array(bnd.xy, dtype=np.float64)
    xy = np.swapaxes(xy, 0, 1)

    # get the 3D boundary
    z = np.full(len(xy), z_min, dtype=np.float64)
    z = np.expand_dims(z, axis=1)
    xyz = np.hstack((xy, z))

    # remove the duplicated points
    xyz = xyz[:-1]

    # get the face indices
    faces = np.arange(len(xyz) + 1)
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
    mesh = polygon.extrude((0, 0, z_max - z_min), capping=True)

    return mesh


def _get_shape_single(tag, shape_type, shape_data):
    """
    Get a Shapely object for different shapes:
        - a trace (multi-segment line)
        - a pad (filled disc)
        - a polygon
    """

    # get the shape
    if shape_type == "pad":
        buffer = 0.5 * shape_data["diameter"]
        coord = shape_data["coord"]

        if len(coord) < 1:
            raise RuntimeError("invalid shape: a pad should contain at least one coordinate: %s" % tag)

        obj = sha.geometry.MultiPoint(coord)
    elif shape_type == "trace":
        buffer = 0.5 * shape_data["width"]
        coord = shape_data["coord"]

        if len(coord) < 2:
            raise RuntimeError("invalid shape: a trace should contain at least two coordinate: %s" % tag)

        obj = sha.geometry.LineString(coord)
    elif shape_type == "polygon":
        buffer = 1.0 * shape_data["buffer"]
        coord_shell = shape_data["coord_shell"]
        coord_holes = shape_data["coord_holes"]

        if len(coord_shell) < 3:
            raise RuntimeError("invalid shape: a polygon should contain at least three coordinate: %s" % tag)
        for coord_holes_tmp in coord_holes:
            if len(coord_holes_tmp) < 3:
                raise RuntimeError("invalid shape: a polygon should contain at least three coordinate: %s" % tag)

        obj = sha.geometry.Polygon(coord_shell, holes=coord_holes)
    else:
        raise ValueError("invalid shape type")

    # add a buffer with a given thickness around the shape
    obj = obj.buffer(buffer, cap_style="round", join_style="round")

    # check if valid
    if not obj.is_valid:
        raise RuntimeError("invalid shape: geometry is ill-formed: %s" % tag)

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
    idx_shape = np.flatnonzero(idx_shape)

    return idx_shape


def _get_idx_voxel(n, idx_shape, stack_idx):
    """
    Find the 3D voxel indices from the 2D image indices.
    The number of layers to be added is arbitrary.
    """

    # get the shape size
    (nx, ny, nz) = n

    # init voxel indices
    idx_voxel = np.empty(0, dtype=np.int64)

    # convert image indices into voxel indices
    for idx in stack_idx:
        # convert indices
        idx_tmp = idx * nx * ny + idx_shape

        # add the indices to the array
        idx_voxel = np.append(idx_voxel, idx_tmp)

    return idx_voxel


def _get_shape_assemble(tag, geometry_shape, simplify, construct):
    """
    Assemble the shapes (for a specified layer).
    """

    # init the shape list
    obj_add = []
    obj_sub = []

    # find the shapes
    for geometry_shape_tmp_tmp in geometry_shape:
        # extract the data
        shape_layer = geometry_shape_tmp_tmp["shape_layer"]
        shape_operation = geometry_shape_tmp_tmp["shape_operation"]
        shape_type = geometry_shape_tmp_tmp["shape_type"]
        shape_data = geometry_shape_tmp_tmp["shape_data"]

        # add the shape
        if tag in shape_layer:
            # get the shape
            obj = _get_shape_single(tag, shape_type, shape_data)

            # add to the list
            if shape_operation == "add":
                obj_add.append(obj)
            elif shape_operation == "sub":
                obj_sub.append(obj)
            else:
                raise ValueError("invalid shape type")

    # assemble the shapes
    obj_add = sha.unary_union(obj_add, grid_size=construct)
    obj_sub = sha.unary_union(obj_sub, grid_size=construct)
    obj = sha.difference(obj_add, obj_sub, grid_size=construct)

    # simplify the shape
    if simplify is not None:
        obj = sha.simplify(obj, simplify, preserve_topology=False)

    return obj


def _get_shape_layer(geometry_shape, stack_tag, simplify, construct):
    """
    Assemble the shapes (for all the layers).
    """

    # init list
    layer_list = []
    obj_list = []

    # get the shapes
    for tag in stack_tag:
        # get the assembled shape
        obj = _get_shape_assemble(tag, geometry_shape, simplify, construct)

        # check that the shape is valid
        if not obj.is_valid:
            raise RuntimeError("invalid shape: geometry is ill-formed: %s" % tag)

        # add the object
        if not obj.is_empty:
            layer_list.append(tag)
            obj_list.append(obj)

    return layer_list, obj_list


def _get_shape_obj(geometry_shape, stack_tag, simplify, construct):
    """
    Create the shapes and set the position in the layer stack.
    Find the bounding box for all the shapes (minimum and maximum coordinates).
    """

    # init shape list
    shape_obj = []

    # init the coordinate (minimum and maximum coordinates)
    xy_min = np.full(2, +np.inf, dtype=np.float64)
    xy_max = np.full(2, -np.inf, dtype=np.float64)

    # create the shapes and find the bounding box
    for tag, geometry_shape_tmp in geometry_shape.items():
        # get the shape (divided per layer)
        (layer_list, obj_list) = _get_shape_layer(geometry_shape_tmp, stack_tag, simplify, construct)

        # find the layer position and add the objects
        for layer, obj in zip(layer_list, obj_list, strict=True):
            # get the stack position
            idx = stack_tag.index(layer)

            # find the bounds
            (x_min, y_min, x_max, y_max) = obj.bounds
            tmp_min = np.array((x_min, y_min), dtype=np.float64)
            tmp_max = np.array((x_max, y_max), dtype=np.float64)

            # update the bounds
            xy_min = np.minimum(xy_min, tmp_min)
            xy_max = np.maximum(xy_max, tmp_max)

            # assign the object
            shape_obj.append({"tag": tag, "idx": idx, "obj": obj})

    return shape_obj, xy_min, xy_max


def _get_layer_stack(layer_stack, dz, cz):
    """
    Parse the layer stack (defined with a list).
    Return the number of layers and the coordinates of the layers.
    """

    # init the list
    stack_n = []
    stack_idx = []
    stack_tag = []

    # get a list with all the layers and the corresponding names
    for layer_stack_tmp in layer_stack:
        # extract the data
        n_layer = layer_stack_tmp["n_layer"]
        tag_layer = layer_stack_tmp["tag_layer"]

        # find the layer indices
        idx_layer = np.arange(np.sum(stack_n), np.sum(stack_n) + n_layer, dtype=np.int64)

        # append the results
        stack_n.append(n_layer)
        stack_idx.append(idx_layer)
        stack_tag.append(tag_layer)

    # get the positions
    stack_pos = np.append(0, np.cumsum(stack_n))
    stack_pos = stack_pos - np.sum(stack_n) / 2

    # check layer tag names
    if not (len(np.unique(stack_tag)) == len(stack_tag)):
        raise RuntimeError("layer tag name should be unique")

    # scale the dimension
    stack_pos *= dz

    # add offset
    if cz is not None:
        stack_pos += cz

    return stack_pos, stack_idx, stack_tag


def _get_domain_def(n, d, c, geometry_shape, stack_idx, shape_obj):
    """
    Voxelize the shapes and assign the indices to a dict.
    """

    # get the voxelization bounds
    xyz_min = c - (n * d) / 2
    xyz_max = c + (n * d) / 2

    # init the domain dict
    domain_def = {}
    for tag in geometry_shape:
        domain_def[tag] = np.empty(0, np.int64)

    # voxelize the shapes
    for shape_obj_tmp in shape_obj:
        # extract the data
        tag = shape_obj_tmp["tag"]
        obj = shape_obj_tmp["obj"]
        idx = shape_obj_tmp["idx"]

        # voxelize and get the indices
        idx_shape = _get_voxelize_shape(n, xyz_min, xyz_max, obj)
        idx_voxel = _get_idx_voxel(n, idx_shape, stack_idx[idx])

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
    d = np.array([dx, dy, dz], dtype=np.float64)
    xyz_min = np.array([x_min, y_min, z_min], dtype=np.float64)
    xyz_max = np.array([x_max, y_max, z_max], dtype=np.float64)

    # geometry size
    c = (xyz_max + xyz_min) / 2

    # extract the number of voxels and the voxel size
    n = np.rint((xyz_max - xyz_min) / d)
    d = (xyz_max - xyz_min) / n

    # cast data
    d = d.astype(np.float64)
    n = n.astype(np.int64)

    # check voxel validity
    if not np.all(d > 0):
        RuntimeError("invalid voxel dimension: should be positive")
    if not np.all(n > 0):
        RuntimeError("invalid voxel number: should be positive")

    return n, d, c


def _get_merge_shape(stack_pos, shape_obj):
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
        idx = shape_obj_tmp["idx"]

        # get the coordinates
        z_min = stack_pos[idx + 0]
        z_max = stack_pos[idx + 1]

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
    simplify = param["simplify"]
    construct = param["construct"]
    xy_min = param["xy_min"]
    xy_max = param["xy_max"]

    # parse layers
    LOGGER.debug("parse the layers")
    (stack_pos, stack_idx, stack_tag) = _get_layer_stack(layer_stack, dz, cz)

    # create the shapes
    LOGGER.debug("create the shapes")
    (shape_obj, xy_min_obj, xy_max_obj) = _get_shape_obj(geometry_shape, stack_tag, simplify, construct)

    # if provided, the specified bounds are used, otherwise the shape bounds are used
    if xy_min is not None:
        xy_min = np.array(xy_min, np.float64)
    else:
        xy_min = xy_min_obj
    if xy_max is not None:
        xy_max = np.array(xy_max, np.float64)
    else:
        xy_max = xy_max_obj

    # geometry size
    LOGGER.debug("get the voxel size")
    (n, d, c) = _get_voxel_size(dx, dy, dz, stack_pos, xy_max, xy_min)

    # init domain definition dict
    domain_def = {}
    for tag in geometry_shape:
        domain_def[tag] = np.empty(0, np.int64)

    # voxelize the shapes and get the indices
    LOGGER.debug("voxelize the shapes")
    domain_def = _get_domain_def(n, d, c, domain_def, stack_idx, shape_obj)

    # merge the shapes representing the original geometry
    LOGGER.debug("merge the shapes")
    reference = _get_merge_shape(stack_pos, shape_obj)

    # cast to lists
    n = n.tolist()
    d = d.tolist()
    c = c.tolist()

    # cast reference mesh
    reference = {
        "faces": np.array(reference.faces, dtype=np.int64),
        "points": np.array(reference.points, dtype=np.float64),
    }

    return n, d, c, domain_def, reference
