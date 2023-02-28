"""
Different functions for extracting PyVista object from the voxel structure:
    - the complete voxel structure (uniform grid)
    - the structure containing non-empty voxels (unstructured grid)
    - the defined point cloud (polydata object)

Afterwards, different variables are associated with the PyVista object:
    - descriptive variables (integers)
    - scalar variables
    - vector variables
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import numpy as np
import numpy.linalg as lna
import pyvista as pv
from pypeec.lib_utils.error import RunError


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


def get_voxel(grid, idx_v):
    """
    Construct a PyVista unstructured grid for the non-empty voxels.
    The indices of the non-empty voxels are provided.
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
    data_point = np.array(data_point, dtype=np.float_)

    # create the point cloud
    point = pv.PolyData(data_point)

    # check that the points are not inside the grid
    surface = voxel.extract_surface()
    selection = point.select_enclosed_points(surface, tolerance=0.0, check_surface=False)
    mask = selection["SelectedPoints"].view(bool)
    if np.any(mask):
        raise RunError("invalid points: points should not be located inside the non-empty voxels.")

    return point


def set_viewer_domain(voxel, idx, domain, connection):
    """
    Add the domain and connected component description to the unstructured grid.
    Integers are used to encode the different tags.
    """

    # sort idx
    idx_sort = np.argsort(idx)
    domain = domain[idx_sort]
    connection = connection[idx_sort]

    # assign the data to the geometry
    voxel["domain"] = domain
    voxel["connection"] = connection

    return voxel


def set_plotter_voxel_material(voxel, idx, material):
    """
    Add the material and source description to the unstructured grid.
    Integers are used to encode the different tags.
    """

    # init the material
    idx_sort = np.argsort(idx)
    material = material[idx_sort]

    # assign the data to the geometry
    voxel["material"] = material

    return voxel


def set_plotter_voxel_scalar(voxel, idx, idx_var, var, name):
    """
    Add a scalar variable to the unstructured grid (complex variable).
    """

    # find the variable indices
    idx_s = np.argsort(idx)
    idx_p = np.searchsorted(idx[idx_s], idx_var)
    idx_var_local = idx_s[idx_p]

    # assign potential (nan for the voxels where the variable is not defined)
    var_all = np.full(len(idx), np.nan+1j*np.nan, dtype=np.complex_)
    var_all[idx_var_local] = var

    # sort the variable
    var_all = var_all[idx_s]

    # assign potential
    voxel[name + "_re"] = np.real(var_all)
    voxel[name + "_im"] = np.imag(var_all)
    voxel[name + "_abs"] = np.abs(var_all)

    return voxel


def set_plotter_voxel_vector(voxel, idx, idx_var, var, name):
    """
    Add a vector variable to the unstructured grid (complex variable).
    The norm (scalar field) and the direction (vector field) are added.
    """

    # find the variable indices
    idx_s = np.argsort(idx)
    idx_p = np.searchsorted(idx[idx_s], idx_var)
    idx_var_local = idx_s[idx_p]

    # assign flux (nan for the voxels where the variable is not defined)
    var_all = np.full((len(idx), 3), np.nan+1j*np.nan, dtype=np.complex_)
    var_all[idx_var_local] = var

    # sort the variable
    var_all = var_all[idx_s]

    # assign the current density norm
    voxel[name + "_norm_abs"] = lna.norm(var_all, axis=1)
    voxel[name + "_norm_re"] = lna.norm(np.real(var_all), axis=1)
    voxel[name + "_norm_im"] = lna.norm(np.imag(var_all), axis=1)

    # assign the current density direction
    voxel[name + "_vec_re"] = np.real(var_all)
    voxel[name + "_vec_im"] = np.imag(var_all)

    return voxel


def set_plotter_magnetic_field(point, H_point):
    """
    Add the magnetic field to the point cloud.
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