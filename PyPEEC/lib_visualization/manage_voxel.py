"""
Different functions for extracting PyVista object from the voxel structure:
    - the complete voxel structure (uniform grid)
    - the structure containing non-empty voxels (unstructured grid)
    - the defined point cloud (polydata object)

For the viewer, create the objects and add the domain definition.

For the plotter, create the objects and add the solution:
    - material description (conductors and sources)
    - resistivity
    - potential
    - current density
    - loss/energy
    - magnetic field
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np
import numpy.linalg as lna
import pyvista as pv
from PyPEEC.lib_utils.error import RunError


def get_grid(n, d, c):
    """
    Construct a PyVista uniform grid for the complete voxel structure.
    """

    # extract the voxel data
    (nx, ny, nz) = n
    (dx, dy, dz) = d
    (cx, cy, cz) = c

    # origin coordinate
    ox = cx-(nx*dx)/2
    oy = cy-(ny*dy)/2
    oz = cz-(nz*dz)/2

    # create a uniform grid for the complete structure
    grid = pv.UniformGrid()

    # set the array size and the voxel size
    grid.origin = (ox, oy, oz)
    grid.dimensions = (nx+1, ny+1, nz+1)
    grid.spacing = (dx, dy, dz)

    return grid


def get_voxel_plotter(grid, idx_vc, idx_vm):
    """
    Construct a PyVista unstructured grid for the non-empty voxels.
    The indices of the non-empty vocels are provided.
    """

    # assemble idx
    idx_v = np.concatenate((idx_vc, idx_vm))
    idx_v = np.sort(idx_v)

    # transform the uniform grid into an unstructured grid (keeping the non-empty voxels)
    voxel = grid.extract_cells(idx_v)

    return voxel, idx_v


def get_voxel_viewer(grid, idx_v):
    """
    Construct a PyVista unstructured grid for the non-empty voxels.
    The indices of the non-empty vocels are provided.
    """

    # assemble idx
    idx_v = np.sort(idx_v)

    # transform the uniform grid into an unstructured grid (keeping the non-empty voxels)
    voxel = grid.extract_cells(idx_v)

    return voxel


def get_point(data_point, voxel):
    """
    Construct a PyVista point cloud (polydata) with the defined points.
    The points cannot be located inside the non-empty voxels.
    """

    # cast the array with the coordinates
    data_point = np.array(data_point, dtype=np.float64)

    # create the point cloud
    point = pv.PolyData(data_point)

    # check that the points are not inside the grid
    surface = voxel.extract_surface()
    selection = point.select_enclosed_points(surface, tolerance=0.0, check_surface=False)
    mask = selection['SelectedPoints'].view(bool)
    if np.any(mask):
        raise RunError("invalid points: points should not be located inside the non-empty voxels.")

    return point


def set_viewer_domain(voxel, idx_v, dom_v, gra_v):
    """
    Add the domains to the unstructured grid.
    Add the connected components to the unstructured grid.
    A fake scalar field is used to encode the domains and connected components.
    """

    # sort idx
    idx_sort = np.argsort(idx_v)
    dom_v = dom_v[idx_sort]
    gra_v = gra_v[idx_sort]

    # assign the extract data to the geometry
    voxel["domain"] = dom_v
    voxel["connection"] = gra_v

    return voxel


def set_plotter_voxel_material(voxel, idx_v, idx_vc, idx_vm, idx_src_c, idx_src_v):
    """
    Add the material description to the unstructured grid.
    The following fake scalar field encoding is used:
        - 0: conducting voxels
        - 1: current source voxels
        - 2: voltage source voxels
    """

    # init the material
    data = np.empty(len(idx_v), dtype=np.int64)

    # find position
    idx_vc_local = np.flatnonzero(np.in1d(idx_v, idx_vc))
    idx_vm_local = np.flatnonzero(np.in1d(idx_v, idx_vm))
    idx_src_c_local = np.flatnonzero(np.in1d(idx_v, idx_src_c))
    idx_src_v_local = np.flatnonzero(np.in1d(idx_v, idx_src_v))

    # assign the voltage and current sources
    data[idx_vc_local] = 1
    data[idx_vm_local] = 2
    data[idx_src_c_local] = 3
    data[idx_src_v_local] = 4

    # assign the extract data to the geometry
    voxel["material"] = data

    return voxel


def set_plotter_voxel_scalar(voxel, idx_v, idx_var, var_pot, name_pot):
    """
    Add the different variables to the unstructured grid:
        - resistivity (scalar field, input variable)
        - potential (scalar field, solved variable)
        - current density (scalar and vector fields, solved variable)
        - loss (scalar field, solved variable)
    """

    # find the variable indices
    idx_s = np.argsort(idx_v)
    idx_p = np.searchsorted(idx_v[idx_s], idx_var)
    idx_var_local = idx_s[idx_p]

    # assign potential (nan for the voxels where the variable is not defined)
    var_pot_all = np.full(len(idx_v), np.nan+1j*np.nan, dtype=np.complex128)
    var_pot_all[idx_var_local] = var_pot

    # assign potential
    voxel[name_pot + "_re"] = np.real(var_pot_all)
    voxel[name_pot + "_im"] = np.imag(var_pot_all)
    voxel[name_pot + "_abs"] = np.abs(var_pot_all)

    return voxel


def set_plotter_voxel_vector(voxel, idx_v, idx_var, var_flow, name_flux):
    """
    Add the different variables to the unstructured grid:
        - resistivity (scalar field, input variable)
        - potential (scalar field, solved variable)
        - current density (scalar and vector fields, solved variable)
        - loss (scalar field, solved variable)
    """

    # find the variable indices
    idx_s = np.argsort(idx_v)
    idx_p = np.searchsorted(idx_v[idx_s], idx_var)
    idx_var_local = idx_s[idx_p]

    # assign flux (nan for the voxels where the variable is not defined)
    var_flux_all = np.full((len(idx_v), 3), np.nan+1j*np.nan, dtype=np.complex128)
    var_flux_all[idx_var_local] = var_flow

    # assign the current density norm
    voxel[name_flux + "_norm_abs"] = lna.norm(var_flux_all, axis=1)
    voxel[name_flux + "_norm_re"] = lna.norm(np.real(var_flux_all), axis=1)
    voxel[name_flux + "_norm_im"] = lna.norm(np.imag(var_flux_all), axis=1)

    # assign the current density direction
    voxel[name_flux + "_vec_re"] = np.real(var_flux_all)
    voxel[name_flux + "_vec_im"] = np.imag(var_flux_all)

    return voxel


def set_plotter_magnetic_field(point, H_point):
    """
    Add the magnetic field (scalar and vector fields, current density) to the point cloud.
    The norm (scalar field) and the direction (vector field) are added.
    """

    # compute the norm
    point["H_norm_abs"] = lna.norm(H_point, axis=1)
    point["H_norm_re"] = lna.norm(np.real(H_point), axis=1)
    point["H_norm_im"] = lna.norm(np.imag(H_point), axis=1)

    # compute the direction
    point["H_vec_re"] = np.real(H_point)
    point["H_vec_im"] = np.imag(H_point)

    return point
