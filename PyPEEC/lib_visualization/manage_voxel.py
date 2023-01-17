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


def get_voxel(grid, idx_v):
    """
    Construct a PyVista unstructured grid for the non-empty voxels.
    The indices of the non-empty vocels are provided.
    """

    # sort idx
    idx_v = np.sort(idx_v)

    # transform the uniform grid into an unstructured grid (keeping the non-empty voxels)
    voxel = grid.extract_cells(idx_v)

    return voxel


def get_point(voxel, data_point):
    """
    Construct a PyVista point cloud with the defined points.
    """

    # create the point cloud
    point = pv.PolyData(data_point)

    # check that the points are not inside the grid
    surface = voxel.extract_surface()
    selection = point.select_enclosed_points(surface)
    mask = selection['SelectedPoints'].view(bool)
    if np.any(mask):
        raise RunError("invalid points: points should not be located inside the non-empty voxels.")

    return point


def get_viewer_domain(domain_def):
    """
    Get the indices of the non-empty voxels.
    Assign a different scalar for each domain.
    """

    # init
    idx_v = np.empty(0, dtype=np.int64)
    dom_v = np.empty(0, dtype=np.int64)

    # get the indices and colors
    counter = 0
    for tag, idx_tmp in domain_def.items():
        # assign the color (n different integer for each domain)
        dom_tmp = np.full(len(idx_tmp), counter, dtype=np.int64)

        # append the indices and colors
        idx_v = np.append(idx_v, idx_tmp)
        dom_v = np.append(dom_v, dom_tmp)
        counter += 1

    return idx_v, dom_v


def get_viewer_tag(voxel, idx_v, dom_v):
    """
    Add the domain tags to the grid as a fake scalar field.
    """

    # sort idx
    idx_sort = np.argsort(idx_v)
    dom_v = dom_v[idx_sort]

    # assign the extract data to the geometry
    voxel["tag"] = dom_v

    return voxel


def get_plotter_tag(voxel, idx_v, idx_src_c, idx_src_v):
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
    idx_sort = np.argsort(idx_v)
    data = data[idx_sort]

    # assign the extract data to the geometry
    voxel["material"] = data

    return voxel


def get_plotter_resistivity(voxel, idx_v, rho_v):
    """
    Add the resistivity (scalar field, input variable) to the unstructured grid.
    """

    # sort idx
    idx_s = np.argsort(idx_v)
    rho_v = rho_v[idx_s]

    # assign data
    voxel["rho"] = rho_v

    return voxel


def get_plotter_potential(voxel, idx_v, V_v):
    """
    Add the potential (scalar field, solved variable) to the unstructured grid.
    """

    # sort idx
    idx_s = np.argsort(idx_v)
    V_v = V_v[idx_s]

    # assign data
    voxel["V_re"] = np.real(V_v)
    voxel["V_im"] = np.imag(V_v)
    voxel["V_abs"] = np.abs(V_v)

    return voxel


def get_plotter_current_density(voxel, idx_v, J_v):
    """
    Add the potential (scalar and vector fields, current density) to the unstructured grid.
    The norm (scalar field) and the direction (vector field) are added.
    """

    # sort idx
    idx_s = np.argsort(idx_v)
    J_v = J_v[idx_s, :]

    # compute the norm
    voxel["J_norm_abs"] = lna.norm(J_v, axis=1)
    voxel["J_norm_re"] = lna.norm(np.real(J_v), axis=1)
    voxel["J_norm_im"] = lna.norm(np.imag(J_v), axis=1)

    # compute the direction, ignore division per zero
    with np.errstate(all="ignore"):
        voxel["J_vec_re"] = np.real(J_v)
        voxel["J_vec_im"] = np.imag(J_v)

    return voxel
