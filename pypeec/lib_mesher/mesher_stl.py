"""
Module for transforming STL files into a 3D voxel structure.
Each STL file corresponds to a domain of the 3D voxel structure.

The voxelization is done with PyVista:
    - using the enclosed point detection
    - with custom test points
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import vtk
import scilogger
import numpy as np
import pyvista as pv
import scipy.sparse as sps
import scipy.special as spe

# get a logger
LOGGER = scilogger.get_logger(__name__, "pypeec")

# prevent VTK to mess up the output
vtk.vtkObject.GlobalWarningDisplayOff()


def _get_load_stl(filename, scale, offset, check):
    """
    Load several STL files and merge the meshes.
    """

    # load the mesh
    try:
        mesh = pv.read(filename, force_ext=".stl")
    except ValueError:
        raise RuntimeError("invalid stl: invalid file: %s" % filename) from None

    # check that the mesh is not empty
    if mesh.n_cells == 0:
        raise RuntimeError("invalid stl: mesh is empty: %s" % filename)

    # check that the mesh is closed
    if check and (mesh.n_open_edges > 0):
        raise RuntimeError("invalid stl: mesh is not closed: %s" % filename)

    # translate the meshes
    mesh = mesh.scale(scale, inplace=True)
    mesh = mesh.translate(offset, inplace=True)

    return mesh


def _get_voxelize_stl(pts, connect, mesh, thr):
    """
    Voxelize a STL mesh with respect to a voxel structure.
    Return the indices of the created voxels.
    """

    # get the point cloud
    cloud = pv.PointSet(pts)

    # voxelize the mesh
    try:
        selection = cloud.select_enclosed_points(mesh, tolerance=0.0, check_surface=False)
    except RuntimeError:
        raise RuntimeError("invalid mesh: mesh cannot be voxelized") from None

    # create a boolean mask
    mask = selection["SelectedPoints"].view(bool)

    # count the number of test points per voxel
    count = connect * mask

    # get the indices of the extracted voxels
    idx_voxel = np.flatnonzero(count >= thr)

    return idx_voxel


def _get_mesh_stl(domain_stl, check):
    """
    Load meshes from STL files and find the minimum and maximum coordinates.
    Find the bounding box for all the meshes (minimum and maximum coordinates).
    """

    # init STL mesh list
    mesh_stl = []
    mesh_all = []

    # init the coordinate (minimum and maximum coordinates)
    xyz_min = np.full(3, +np.inf, dtype=np.float64)
    xyz_max = np.full(3, -np.inf, dtype=np.float64)

    # load the STL files and find the bounding box
    for tag, domain_stl_tmp in domain_stl.items():
        for domain_stl_tmp_tmp in domain_stl_tmp:
            # extract the data
            scale = domain_stl_tmp_tmp["scale"]
            offset = domain_stl_tmp_tmp["offset"]
            filename = domain_stl_tmp_tmp["filename"]

            # load the STL
            mesh = _get_load_stl(filename, scale, offset, check)

            # find the bounds
            (x_min, x_max, y_min, y_max, z_min, z_max) = mesh.bounds
            tmp_min = np.array((x_min, y_min, z_min), dtype=np.float64)
            tmp_max = np.array((x_max, y_max, z_max), dtype=np.float64)

            # update the bounds
            xyz_min = np.minimum(xyz_min, tmp_min)
            xyz_max = np.maximum(xyz_max, tmp_max)

            # assign the mesh
            mesh_all.append(mesh)
            mesh_stl.append({"tag": tag, "mesh": mesh})

    # merge all the meshes
    reference = pv.MultiBlock(mesh_all)
    reference = reference.combine().extract_surface()

    return mesh_stl, reference, xyz_min, xyz_max


def _get_voxel_size(d, xyz_max, xyz_min):
    """
    Get the parameters (size, dimension, and center) of the voxel structure.
    """

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


def _get_point_test(d, pts):
    """
    Get the test point coordinates for a single voxel.
    """

    # extract the voxel data
    (dx, dy, dz) = d

    # get the quadrature points
    (v_vec, w_vec) = spe.roots_legendre(pts)
    x_vec = v_vec * dx / 2
    y_vec = v_vec * dy / 2
    z_vec = v_vec * dz / 2

    # span the voxel points
    [x_vec, y_vec, z_vec] = np.meshgrid(x_vec, y_vec, z_vec)
    x_vec = x_vec.flatten()
    y_vec = y_vec.flatten()
    z_vec = z_vec.flatten()

    # span the voxel weights
    [wx_vec, wy_vec, wz_vec] = np.meshgrid(w_vec, w_vec, w_vec)
    wx_vec = wx_vec.flatten()
    wy_vec = wy_vec.flatten()
    wz_vec = wz_vec.flatten()

    # compute the points
    pts_test = np.stack((x_vec, y_vec, z_vec), axis=1)

    # compute the weights
    wgt_test = (wx_vec * wy_vec * wz_vec) / 8

    return pts_test, wgt_test


def _get_point_grid(n, d, c):
    """
    Get the center point coordinates for the single structure.
    """

    # extract the voxel data
    (nx, ny, nz) = n
    (dx, dy, dz) = d
    (cx, cy, cz) = c

    # get total size
    nv = np.prod(n)

    # point vectors
    x_vec = cx + dx * (np.arange(nx, dtype=np.float64) - ((nx - 1) / 2))
    y_vec = cy + dy * (np.arange(ny, dtype=np.float64) - ((ny - 1) / 2))
    z_vec = cz + dz * (np.arange(nz, dtype=np.float64) - ((nz - 1) / 2))

    # all the indices
    idx_linear = np.arange(0, nv, dtype=np.int64)

    # convert linear indices into tensor indices
    (idx_x, idx_y, idx_z) = np.unravel_index(idx_linear, n, order="F")

    # span the voxel points
    x_vec = x_vec[idx_x]
    y_vec = y_vec[idx_y]
    z_vec = z_vec[idx_z]

    # get the points
    pts_grid = np.stack((x_vec, y_vec, z_vec), axis=1)

    return pts_grid


def _get_voxel_structure(pts_test, wgt_test, pts_grid):
    """
    Get the test points for the complete voxel structure.
    Assign the test points to the voxels.
    """

    # span the test points
    idx_test = np.arange(len(pts_test), dtype=np.int64)
    idx_grid = np.arange(len(pts_grid), dtype=np.int64)
    [idx_grid, idx_test] = np.meshgrid(idx_grid, idx_test, indexing="ij")
    idx_test = idx_test.flatten()
    idx_grid = idx_grid.flatten()

    # expand the test points
    pts = pts_test[idx_test] + pts_grid[idx_grid]

    # assign the test points to the voxels
    data = np.tile(wgt_test, len(pts_grid))
    idx_col = np.arange(len(pts), dtype=np.int64)
    idx_row = np.arange(len(pts_grid), dtype=np.int64)
    idx_row = np.repeat(idx_row, len(pts_test))
    connect = sps.csc_matrix((data, (idx_row, idx_col)), shape=(len(pts_grid), len(pts)), dtype=np.float64)

    return pts, connect


def _get_domain_def(pts, connect, domain_stl, mesh_stl, thr):
    """
    Voxelize meshes and assign the indices to a dict.
    """

    # init the domain dict
    domain_def = {}
    for tag in domain_stl:
        domain_def[tag] = np.empty(0, np.int64)

    # voxelize the meshes
    for mesh_stl_tmp in mesh_stl:
        # extract the data
        tag = mesh_stl_tmp["tag"]
        mesh = mesh_stl_tmp["mesh"]

        # voxelize and get the indices
        idx_voxel = _get_voxelize_stl(pts, connect, mesh, thr)

        # append the indices into the corresponding domain
        domain_def[tag] = np.append(domain_def[tag], idx_voxel)

    # remove duplicates
    for tag, idx_voxel in domain_def.items():
        idx_voxel = np.unique(idx_voxel)
        LOGGER.debug("%s: n_voxel = %d" % (tag, len(idx_voxel)))
        domain_def[tag] = idx_voxel

    return domain_def


def get_mesh(param, domain_stl):
    """
    Transform STL files into a 3D voxel structure.
    Each STL file corresponds to a domain of the 3D voxel structure.
    """

    # extract the data
    d = param["d"]
    xyz_min = param["xyz_min"]
    xyz_max = param["xyz_max"]
    check = param["check"]
    thr = param["thr"]
    pts = param["pts"]

    # load the mesh and get the STL bounds
    LOGGER.debug("load STL files")
    (mesh_stl, reference, xyz_min_stl, xyz_max_stl) = _get_mesh_stl(domain_stl, check)

    # if provided, the specified bounds are used, otherwise the mesh bounds are used
    if xyz_min is not None:
        xyz_min = np.array(xyz_min, np.float64)
    else:
        xyz_min = xyz_min_stl
    if xyz_max is not None:
        xyz_max = np.array(xyz_max, np.float64)
    else:
        xyz_max = xyz_max_stl

    # geometry size
    LOGGER.debug("get the voxel size")
    (n, d, c) = _get_voxel_size(d, xyz_max, xyz_min)

    # get the test points
    LOGGER.debug("get the test points")
    (pts_test, wgt_test) = _get_point_test(d, pts)

    # get the voxel points
    LOGGER.debug("get the voxel points")
    pts_grid = _get_point_grid(n, d, c)

    # get the voxel structure
    LOGGER.debug("get the voxel structure")
    (pts, connect) = _get_voxel_structure(pts_test, wgt_test, pts_grid)

    # voxelize the meshes and get the indices
    LOGGER.debug("voxelize STL files")
    domain_def = _get_domain_def(pts, connect, domain_stl, mesh_stl, thr)

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
