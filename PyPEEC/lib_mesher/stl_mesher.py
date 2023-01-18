"""
Module for transforming STL files into a 3D voxel structure.
Each STL file corresponds to a domain of the 3D voxel structure.

If a voxel is located between two domains, it can be assigned to both domains.
This creates a conflict as the voxel to domains mapping is not anymore a bijection.
Therefore, such conflicts are detected and resolved.

The voxelization is done with PyVista.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np
import pyvista as pv
from PyPEEC.lib_utils.error import RunError


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
    grid["idx"] = np.arange(np.prod(n), dtype=np.int64)

    # cast is required for voxelization
    grid = grid.cast_to_unstructured_grid()

    return grid


def get_voxelize(grid, mesh):
    """
    Voxelixe a STL mesh with respect to an uniform grid.
    Return the indices of the created voxels.
    """

    # voxelize the mesh
    try:
        selection = grid.select_enclosed_points(mesh, tolerance=0.0, check_surface=True)
    except RuntimeError:
        raise RunError("invalid mesh: mesh cannot be voxelized")

    # create a boolean mask
    mask = selection['SelectedPoints'].view(bool)

    # transform the grid into an unstructured grid (keeping the non-empty voxels)
    voxel = grid.extract_points(mask)

    # check for empty voxels
    if voxel.n_cells == 0:
        raise RunError("invalid mesh: empty voxel structure")

    # get the indices of the extracted voxels
    idx = voxel["idx"]

    return idx


def _get_idx_stl(grid, mesh_stl):
    """
    Voxelize STL meshes and assign the indices to a dict.
    """

    # init the domain dict
    domain_def = dict()

    # load the STL files
    for tag, mesh in mesh_stl.items():
        # voxelize and get the indices
        idx = get_voxelize(grid, mesh)

        # assign the indices to the domain
        domain_def[tag] = idx

    return domain_def


def _get_load_stl(domain_stl):
    """
    Load meshes from STL files and find the minimum and maximum coordinates.
    The minimum and maximum coordinates defines a bounding box for all the meshes.
    """

    # init STL mesh dict
    mesh_stl = dict()

    # init the coordinate (minimum and maximum coordinates)
    coord_min = np.full(3, +np.inf, dtype=np.float64)
    coord_max = np.full(3, -np.inf, dtype=np.float64)

    # load the STL files and find the bounding box
    for tag, filename in domain_stl.items():
        # load the STL
        try:
            mesh = pv.read(filename, force_ext=".stl")
        except ValueError:
            raise RunError("invalid stl: invalid file content: %s" % filename)

        # find the bounds
        (x_min, x_max, y_min, y_max, z_min, z_max) = mesh.bounds
        tmp_min = np.array((x_min, y_min, z_min), dtype=np.float64)
        tmp_max = np.array((x_max, y_max, z_max), dtype=np.float64)

        # update the bounds
        coord_min = np.minimum(coord_min, tmp_min)
        coord_max = np.maximum(coord_max, tmp_max)

        # assign the mesh
        mesh_stl[tag] = mesh

    return mesh_stl, coord_min, coord_max


def _get_solve_overlap(domain_def, domain_ref, domain_fix):
    """
    Detect and remove shared indices (conflict) between two domains.
    The conflict is solved in the following way:
        - the reference domain remains unchanged
        - the shared indices are removed from the domain to be fixed
    """

    # get the indices
    idx_ref = domain_def[domain_ref]
    idx_fix = domain_def[domain_fix]

    # resolve the conflict
    idx_fix = np.setdiff1d(idx_fix, idx_ref)

    # update the domain indices
    domain_def[domain_fix] = idx_fix

    return domain_def


def get_mesh(n, pts_min, pts_max, domain_stl):
    """
    Transform STL files into a 3D voxel structure.
    Each STL file corresponds to a domain of the 3D voxel structure.
    """

    # load the mesh and get the STL bounds
    (mesh_stl, coord_min, coord_max) = _get_load_stl(domain_stl)

    # cast to array
    n = np.array(n, np.int64)
    pts_min = np.array(pts_min, np.float64)
    pts_max = np.array(pts_max, np.float64)

    # if provided, the user specified bounds are used, otherwise the STL bounds
    pts_min = np.array(pts_min, np.float64)
    pts_max = np.array(pts_max, np.float64)
    idx_replace_min = np.isnan(pts_min)
    idx_replace_max = np.isnan(pts_max)
    pts_min[idx_replace_min] = coord_min[idx_replace_min]
    pts_max[idx_replace_max] = coord_max[idx_replace_max]

    # extract the voxel size
    d = (pts_max-pts_min)/n

    # extract the center
    c = (pts_max+pts_min)/2

    # check voxel validity
    if not np.all(d > 0):
        RunError("invalid voxel dimension: should be positive")

    # get the uniform grid
    grid = _get_grid(n, d, c)

    # voxelize the meshes and get the indices
    domain_def = _get_idx_stl(grid, mesh_stl)

    # cast back the voxel size and center to a list
    d = d.tolist()
    c = c.tolist()

    return d, c, domain_def


def get_conflict(domain_def, domain_conflict):
    """
    Detect and remove shared indices (conflict) between domains.
    The direction of the conflict resolution (between two domains) is specified by the user.
    At the end, check that all shared indices have been removed.
    """

    # resolve the conflicts for all the specified domain pairs
    for dat_tmp in domain_conflict:
        # extract data
        domain_ref = dat_tmp["domain_ref"]
        domain_fix = dat_tmp["domain_fix"]

        # solve the conflict
        domain_def = _get_solve_overlap(domain_def, domain_ref, domain_fix)

    # assemble all the indices
    idx_all = np.array([], dtype=np.int64)
    for idx in domain_def.values():
        idx_all = np.append(idx_all, idx)

    # check that all the conflicts are resolved
    if not (len(np.unique(idx_all)) == len(idx_all)):
        raise RunError("invalid domain: domain indices should be unique")

    return domain_def
