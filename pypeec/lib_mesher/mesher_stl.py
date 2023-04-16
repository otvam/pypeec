"""
Module for transforming STL files into a 3D voxel structure.
Each STL file corresponds to a domain of the 3D voxel structure.

If a voxel is located between two domains, it can be assigned to both domains.
This creates a conflict as the voxel to domains mapping is not anymore a bijection.
Such conflicts should be resolved with the conflict resolution rules.

The voxelization is done with PyVista.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import vtk
import numpy as np
import pyvista as pv
from pypeec import utils_log
from pypeec import config
from pypeec.error import RunError

# get a logger
LOGGER = utils_log.get_logger("STL")

# get config
NP_TYPES = config.NP_TYPES

# prevent VTK to mess up the output
vtk.vtkObject.GlobalWarningDisplayOff()


def _get_grid(n, d, c):
    """
    Construct a PyVista uniform grid for the complete voxel structure.
    The grid is located around the STL meshes to be voxelized.
    """

    # create a uniform grid for the complete structure
    grid = pv.UniformGrid()

    # set the array size and the voxel size
    grid.origin = c-(n*d)/2
    grid.dimensions = n+1
    grid.spacing = d

    # add indices for tracking the voxels after voxelization
    grid["idx"] = np.arange(np.prod(n), dtype=NP_TYPES.INT)

    # cast is required for voxelization
    grid = grid.cast_to_unstructured_grid()

    return grid


def _get_voxelize(grid, tag, mesh):
    """
    Voxelize an STL mesh with respect to a uniform grid.
    Return the indices of the created voxels.
    """

    # voxelize the mesh
    try:
        selection = grid.select_enclosed_points(mesh, tolerance=0.0, check_surface=True)
    except RuntimeError:
        raise RunError("invalid mesh: mesh cannot be voxelized: %s" % tag)

    # create a boolean mask
    mask = selection["SelectedPoints"].view(bool)

    # find the voxel indices
    if np.any(mask):
        # transform the grid into an unstructured grid (keeping the non-empty voxels)
        voxel = grid.extract_points(mask)

        # get the indices of the extracted voxels
        idx = voxel["idx"]
    else:
        idx = np.array([], dtype=NP_TYPES.INT)

    return idx


def _get_idx_stl(grid, mesh_stl):
    """
    Voxelize STL meshes and assign the indices to a dict.
    """

    # init the domain dict
    domain_def = {}

    # load the STL files
    for tag, mesh in mesh_stl.items():
        # voxelize and get the indices
        idx = _get_voxelize(grid, tag, mesh)

        # display number of voxels
        LOGGER.debug("%s: n_voxel = %d" % (tag, len(idx)))

        # assign the indices to the domain
        domain_def[tag] = idx

    return domain_def


def _get_merge_stl(c, c_stl, mesh_stl):
    """
    Merge the STL files into a single mesh.
    Translate the mesh with the provided origin.
    """

    # merge the meshes
    mesh_list = list(mesh_stl.values())
    reference = pv.MultiBlock(mesh_list).combine().extract_surface()

    # place at the new origin
    reference = reference.translate(c-c_stl, inplace=True)

    return reference


def _get_load_stl(offset, filename_list):
    """
    Load several STL files and merge the meshes.
    """

    # list for the meshes
    mesh_list = []

    # load the files
    for filename in filename_list:
        # load the file
        try:
            mesh = pv.read(filename, force_ext=".stl")
        except ValueError:
            raise RunError("invalid stl: invalid file type: %s" % filename)

        # check that the file is valid
        if mesh.n_cells == 0:
            raise RunError("invalid stl: invalid file content: %s" % filename)

        # store the loaded mesh
        mesh_list.append(mesh)

    # merge the meshes
    mesh = pv.MultiBlock(mesh_list).combine().extract_surface()

    # translate the meshes
    mesh = mesh.translate(offset, inplace=True)

    return mesh


def _get_mesh_stl(domain_stl):
    """
    Load meshes from STL files and find the minimum and maximum coordinates.
    The minimum and maximum coordinates defines a bounding box for all the meshes.
    """

    # init STL mesh dict
    mesh_stl = {}

    # init the coordinate (minimum and maximum coordinates)
    xyz_min = np.full(3, +np.inf, dtype=NP_TYPES.FLOAT)
    xyz_max = np.full(3, -np.inf, dtype=NP_TYPES.FLOAT)

    # load the STL files and find the bounding box
    for tag, dat_tmp in domain_stl.items():
        # extract data
        offset = dat_tmp["offset"]
        filename_list = dat_tmp["filename_list"]

        # load the STL
        mesh = _get_load_stl(offset, filename_list)

        # display the mesh size
        n_face = mesh.n_faces
        n_vertice = mesh.n_points
        LOGGER.debug("%s: n_face = %d / n_vertice = %d" % (tag, n_face, n_vertice))

        # find the bounds
        (x_min, x_max, y_min, y_max, z_min, z_max) = mesh.bounds
        tmp_min = np.array((x_min, y_min, z_min), dtype=NP_TYPES.FLOAT)
        tmp_max = np.array((x_max, y_max, z_max), dtype=NP_TYPES.FLOAT)

        # update the bounds
        xyz_min = np.minimum(xyz_min, tmp_min)
        xyz_max = np.maximum(xyz_max, tmp_max)

        # assign the mesh
        mesh_stl[tag] = mesh

    return mesh_stl, xyz_min, xyz_max


def get_mesh(n, d, c, sampling, xyz_min, xyz_max, domain_stl):
    """
    Transform STL files into a 3D voxel structure.
    Each STL file corresponds to a domain of the 3D voxel structure.
    """

    # load the mesh and get the STL bounds
    LOGGER.debug("load STL files")
    (mesh_stl, xyz_min_stl, xyz_max_stl) = _get_mesh_stl(domain_stl)

    # if provided, the user specified bounds are used, otherwise the STL bounds
    if xyz_min is None:
        xyz_min = xyz_min_stl
    else:
        xyz_min = np.array(xyz_min, NP_TYPES.FLOAT)
    if xyz_max is None:
        xyz_max = xyz_max_stl
    else:
        xyz_max = np.array(xyz_max, NP_TYPES.FLOAT)

    # extract the number of voxels
    if sampling == "number":
        n = np.array(n, dtype=NP_TYPES.INT)
    elif sampling == "dimension":
        d = np.array(d, dtype=NP_TYPES.FLOAT)
        n = np.rint((xyz_max-xyz_min)/d)
        n = n.astype(NP_TYPES.INT)
    else:
        raise ValueError("inconsistent definition of the voxel number/size")

    # get the voxel size
    d = (xyz_max-xyz_min)/n

    # check voxel validity
    if not np.all(d > 0):
        RunError("invalid voxel dimension: should be positive")
    # check voxel validity
    if not np.all(n > 0):
        RunError("invalid voxel number: should be positive")

    # extract the center
    c_stl = (xyz_max+xyz_min)/2

    # get the uniform grid
    grid = _get_grid(n, d, c_stl)

    # voxelize the meshes and get the indices
    LOGGER.debug("voxelize STL files")
    domain_def = _get_idx_stl(grid, mesh_stl)

    # if provided, the user specified voxel center is used, otherwise the geometrical center
    if c is None:
        c = c_stl
    else:
        c = np.array(c, NP_TYPES.FLOAT)

    # merge meshes
    reference = _get_merge_stl(c, c_stl, mesh_stl)

    # cast to lists
    n = n.tolist()
    d = d.tolist()
    c = c.tolist()

    return n, d, c, domain_def, reference
