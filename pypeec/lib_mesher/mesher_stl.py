"""
Module for transforming STL files into a 3D voxel structure.
Each STL file corresponds to a domain of the 3D voxel structure.

The voxelization is done with PyVista.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import vtk
import scilogger
import numpy as np
import pyvista as pv

# get a logger
LOGGER = scilogger.get_logger(__name__, "pypeec")

# prevent VTK to mess up the output
vtk.vtkObject.GlobalWarningDisplayOff()


def _get_load_stl(scale, offset, filename):
    """
    Load several STL files and merge the meshes.
    """

    # load the mesh
    try:
        mesh = pv.read(filename, force_ext=".stl")
    except ValueError:
        raise RuntimeError("invalid stl: invalid file: %s" % filename) from None

    # check that the file is valid
    if mesh.n_cells == 0:
        raise RuntimeError("invalid stl: invalid file content: %s" % filename)

    # translate the meshes
    mesh = mesh.scale(scale, inplace=True)
    mesh = mesh.translate(offset, inplace=True)

    return mesh


def _get_voxelize_stl(grid, mesh):
    """
    Voxelize an STL mesh with respect to a uniform grid.
    Return the indices of the created voxels.
    """

    # voxelize the mesh
    try:
        selection = grid.select_enclosed_points(mesh, tolerance=0.0, check_surface=True)
    except RuntimeError:
        raise RuntimeError("invalid mesh: mesh cannot be voxelized") from None

    # create a boolean mask
    mask = selection["SelectedPoints"].view(bool)

    # find the voxel indices
    if np.any(mask):
        # transform the grid into an unstructured grid (keeping the non-empty voxels)
        voxel = grid.extract_points(mask)

        # get the indices of the extracted voxels
        idx_voxel = voxel["idx"]
    else:
        idx_voxel = np.empty(0, dtype=np.int64)

    return idx_voxel


def _get_mesh_stl(domain_stl):
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
            mesh = _get_load_stl(scale, offset, filename)

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
    c = (xyz_max+xyz_min)/2

    # extract the number of voxels and the voxel size
    n = np.rint((xyz_max-xyz_min)/d)
    d = (xyz_max-xyz_min)/n

    # cast data
    d = d.astype(np.float64)
    n = n.astype(np.int64)

    # check voxel validity
    if not np.all(d > 0):
        RuntimeError("invalid voxel dimension: should be positive")
    # check voxel validity
    if not np.all(n > 0):
        RuntimeError("invalid voxel number: should be positive")

    return n, d, c


def _get_voxel_grid(n, d, c):
    """
    Construct a PyVista uniform grid for the complete voxel structure.
    The grid is located around the STL meshes to be voxelized.
    """

    # create a uniform grid for the complete structure
    grid = pv.ImageData()

    # set the array size and the voxel size
    grid.origin = c-(n*d)/2
    grid.dimensions = n+1
    grid.spacing = d

    # add indices for tracking the voxels after voxelization
    grid["idx"] = np.arange(np.prod(n), dtype=np.int64)

    # cast is required for voxelization
    grid = grid.cast_to_unstructured_grid()

    return grid


def _get_domain_def(grid, domain_stl, mesh_stl):
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
        idx_voxel = _get_voxelize_stl(grid, mesh)

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

    # load the mesh and get the STL bounds
    LOGGER.debug("load STL files")
    (mesh_stl, reference, xyz_min_stl, xyz_max_stl) = _get_mesh_stl(domain_stl)

    # if provided, the specified bounds are used, otherwise the STL bounds are used
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

    # get the uniform grid
    LOGGER.debug("get the voxel grid")
    grid = _get_voxel_grid(n, d, c)

    # voxelize the meshes and get the indices
    LOGGER.debug("voxelize STL files")
    domain_def = _get_domain_def(grid, domain_stl, mesh_stl)

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
