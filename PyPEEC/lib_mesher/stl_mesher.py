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


def _get_voxelize(grid, tag, mesh):
    """
    Voxelize a STL mesh with respect to a uniform grid.
    Return the indices of the created voxels.
    """

    # voxelize the mesh
    try:
        selection = grid.select_enclosed_points(mesh, tolerance=0.0, check_surface=True)
    except RuntimeError:
        raise RunError("invalid mesh: mesh cannot be voxelized: %s" % tag)

    # create a boolean mask
    mask = selection['SelectedPoints'].view(bool)

    # transform the grid into an unstructured grid (keeping the non-empty voxels)
    voxel = grid.extract_points(mask)

    # get the surface of the new geometry
    surface = voxel.extract_surface()

    # check for empty voxels
    if voxel.n_cells == 0:
        raise RunError("invalid mesh: empty voxel structure: %s" % tag)
    if surface.n_open_edges > 0:
        raise RunError("invalid mesh: surface is not closed: %s" % tag)

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
        idx = _get_voxelize(grid, tag, mesh)

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
    pts_min = np.full(3, +np.inf, dtype=np.float64)
    pts_max = np.full(3, -np.inf, dtype=np.float64)

    # load the STL files and find the bounding box
    for tag, filename in domain_stl.items():
        # load the STL
        try:
            mesh = pv.read(filename, force_ext=".stl")
        except ValueError:
            raise RunError("invalid stl: invalid file content: %s" % tag)

        # find the bounds
        (x_min, x_max, y_min, y_max, z_min, z_max) = mesh.bounds
        tmp_min = np.array((x_min, y_min, z_min), dtype=np.float64)
        tmp_max = np.array((x_max, y_max, z_max), dtype=np.float64)

        # update the bounds
        pts_min = np.minimum(pts_min, tmp_min)
        pts_max = np.maximum(pts_max, tmp_max)

        # assign the mesh
        mesh_stl[tag] = mesh

    return mesh_stl, pts_min, pts_max


def _get_solve_overlap(domain_def, domain_resolve, domain_keep):
    """
    Detect and remove shared indices (conflict) between two domains.
    The conflict is solved in the following way:
        - the reference domain remains unchanged
        - the shared indices are removed from the domain to be fixed
    """

    # get the indices
    idx_keep = domain_def[domain_keep]
    idx_resolve = domain_def[domain_resolve]

    # resolve the conflict
    idx_resolve = np.setdiff1d(idx_resolve, idx_keep)

    # update the domain indices
    domain_def[domain_resolve] = idx_resolve

    return domain_def


def get_mesh(n, d, c, pts_min, pts_max, domain_stl):
    """
    Transform STL files into a 3D voxel structure.
    Each STL file corresponds to a domain of the 3D voxel structure.
    """

    # load the mesh and get the STL bounds
    (mesh_stl, pts_min_stl, pts_max_stl) = _get_load_stl(domain_stl)

    # if provided, the user specified bounds are used, otherwise the STL bounds
    if pts_min is None:
        pts_min = pts_min_stl
    else:
        pts_min = np.array(pts_min, np.float64)
    if pts_max is None:
        pts_max = pts_max_stl
    else:
        pts_max = np.array(pts_max, np.float64)

    # extract the number of voxels
    if (n is not None) and (d is None):
        n = np.array(n, dtype=np.int64)
    elif (n is None) and (d is not None):
        d = np.array(d, dtype=np.float64)
        n = np.rint((pts_max-pts_min)/d)
        n = n.astype(np.int64)
    else:
        raise ValueError("inconsistent definition of the voxel number/size")

    # get the voxel size
    d = (pts_max-pts_min)/n

    # check voxel validity
    if not np.all(d > 0):
        RunError("invalid voxel dimension: should be positive")
    # check voxel validity
    if not np.all(n > 0):
        RunError("invalid voxel number: should be positive")

    # extract the center
    c_stl = (pts_max+pts_min)/2

    # get the uniform grid
    grid = _get_grid(n, d, c_stl)

    # voxelize the meshes and get the indices
    domain_def = _get_idx_stl(grid, mesh_stl)

    # if provided, the user specified voxel center is used, otherwise the geometrical center
    if c is None:
        c = pts_min_stl

    # cast to lists
    n = n.tolist()
    d = d.tolist()
    c = c.tolist()

    return n, d, c, domain_def


def get_conflict(domain_def, domain_conflict):
    """
    Detect and remove shared indices (conflict) between domains.
    The direction of the conflict resolution (between two domains) is specified by the user.
    At the end, check that all shared indices have been removed.
    """

    # resolve the conflicts for all the specified domain pairs
    for domain_conflict_tmp in domain_conflict:
        # extract data
        domain_resolve = domain_conflict_tmp["domain_resolve"]
        domain_keep = domain_conflict_tmp["domain_keep"]

        # solve the conflict
        domain_def = _get_solve_overlap(domain_def, domain_resolve, domain_keep)

    # assemble all the indices
    idx_all = np.array([], dtype=np.int64)
    for idx in domain_def.values():
        idx_all = np.append(idx_all, idx)

    # check that all the conflicts are resolved
    if not (len(np.unique(idx_all)) == len(idx_all)):
        raise RunError("invalid domain: domain indices should be unique")

    return domain_def
