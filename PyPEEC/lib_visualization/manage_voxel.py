"""
Different functions for extracting PyVista grids from the voxel structure.

For the viewer, create the grid and add the domain definition

For the plotter, create the grid and add the solution:
    - material description (conductors and sources)
    - resistivity
    - potential
    - current density)
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np
import numpy.linalg as lna
import pyvista as pv
from PyPEEC.lib_utils.error import RunError


def get_grid(n, d, ori):
    """
    Construct a PyVista uniform grid for the complete voxel structure.
    """

    # extract the voxel data
    (nx, ny, nz) = n
    (dx, dy, dz) = d
    (orix, oriy, oriz) = ori

    # create a uniform grid for the complete structure
    grid = pv.UniformGrid()

    # set the array size and the voxel size
    grid.origin = (orix, oriy, oriz)
    grid.dimensions = (nx+1, ny+1, nz+1)
    grid.spacing = (dx, dy, dz)

    return grid


def get_geom_viewer(grid, domain_def):
    """
    Construct a PyVista unstructured grid for the non-empty voxels.
    Add the domain tags to the grid as a fake scalar field.
    """

    # init
    idx_domain = np.empty(0, dtype=np.int64)
    color_domain = np.empty(0, dtype=np.int64)

    # get the indices and colors
    counter = 0
    for tag, idx in domain_def.items():
        # assign the color (n different integer for each domain)
        color = np.full(len(idx), counter, dtype=np.int64)

        # append the indices and colors
        idx_domain = np.append(idx_domain, idx)
        color_domain = np.append(color_domain, color)
        counter += 1

    # sort idx
    idx_sort = np.argsort(idx_domain)
    idx_domain = idx_domain[idx_sort]
    color_domain = color_domain[idx_sort]

    # transform the uniform grid into an unstructured grid (keeping the non-empty voxels)
    geom = grid.extract_cells(idx_domain)

    # assign the colors
    geom["tag"] = color_domain

    return geom


def get_cloud_viewer(geom, data_point):
    """
    Construct a PyVista point cloud with the defined points.
    Add the point tags to the cloud as a fake scalar field.
    """

    # init
    coord_point = np.empty((0, 3), dtype=np.float64)
    color_point = np.empty(0, dtype=np.int64)

    # get the indices and colors
    counter = 0
    for tag, coord in data_point.items():
        # add the array
        coord = np.array(coord, dtype=np.float64)

        # assign the color (n different integer for each domain)
        color = np.full(len(coord), counter, dtype=np.int64)

        # append the indices and colors
        coord_point = np.concatenate((coord_point, coord), axis=0, dtype=np.float64)
        color_point = np.append(color_point, color)
        counter += 1

    # create the point cloud
    cloud = pv.PolyData(coord_point)

    # check that the points are not inside the grid
    selection = cloud.select_enclosed_points(geom.extract_surface())
    mask = selection['SelectedPoints'].view(bool)
    if np.any(mask):
        raise RunError("invalid points: points should not be located inside the non-empty voxels.")

    # assign the colors
    cloud["tag"] = color_point

    return cloud


def get_geom_plotter(grid, idx_v):
    """
    Construct a PyVista unstructured grid for the non-empty voxels.
    The indices of the non-empty vocels are provided.
    """

    # sort idx
    idx_v = np.sort(idx_v)

    # transform the uniform grid into an unstructured grid (keeping the non-empty voxels)
    geom = grid.extract_cells(idx_v)

    return geom


def get_material(geom, idx_v, idx_src_c, idx_src_v):
    """
    Add the material description (scalar field, input variable) to the unstructured grid.
    The following encoding is used:
        - 0: conducting voxels
        - 1: current source voxels
        - 2: voltage source voxels
    """

    # assign conductors
    data = np.zeros(len(idx_v), dtype=np.float64)

    # get the local source indices
    idx_src_c_local = np.flatnonzero(np.in1d(idx_v, idx_src_c))
    idx_src_v_local = np.flatnonzero(np.in1d(idx_v, idx_src_v))

    # assign the voltage and current sources
    data[idx_src_c_local] = 1
    data[idx_src_v_local] = 2

    # sort idx
    idx_s = np.argsort(idx_v)
    data = data[idx_s]

    # assign the extract data to the geometry
    geom["material"] = data

    return geom


def get_resistivity(geom, idx_v, rho_v):
    """
    Add the resistivity (scalar field, input variable) to the unstructured grid.
    """

    # sort idx
    idx_s = np.argsort(idx_v)
    rho_v = rho_v[idx_s]

    # assign data
    geom["rho"] = rho_v

    return geom


def get_potential(geom, idx_v, V_v):
    """
    Add the potential (scalar field, solved variable) to the unstructured grid.
    """

    # sort idx
    idx_s = np.argsort(idx_v)
    V_v = V_v[idx_s]

    # assign data
    geom["V_re"] = np.real(V_v)
    geom["V_im"] = np.imag(V_v)
    geom["V_abs"] = np.abs(V_v)

    return geom


def get_current_density(geom, idx_v, J_v):
    """
    Add the potential (scalar and vector fields, current density) to the unstructured grid.
    The norm (scalar field) and the direction (vector field) are added.
    """

    # sort idx
    idx_s = np.argsort(idx_v)
    J_v = J_v[idx_s, :]

    # compute the norm
    geom["J_norm_abs"] = lna.norm(J_v, axis=1)
    geom["J_norm_re"] = lna.norm(np.real(J_v), axis=1)
    geom["J_norm_im"] = lna.norm(np.imag(J_v), axis=1)

    # compute the direction, ignore division per zero
    with np.errstate(all="ignore"):
        geom["J_vec_re"] = np.real(J_v)
        geom["J_vec_im"] = np.imag(J_v)

    return geom
