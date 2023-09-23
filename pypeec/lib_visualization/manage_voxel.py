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
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import numpy as np
import numpy.linalg as lna
import pyvista as pv
from pypeec import config
from pypeec.error import RunError

# get config
NP_TYPES = config.NP_TYPES


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
    grid = pv.ImageData()

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
    data_point = np.array(data_point, dtype=NP_TYPES.FLOAT)

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

    # get sorted indices
    idx_sort = np.argsort(idx).astype(NP_TYPES.INT)

    # sort data
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

    # get sorted indices
    idx_sort = np.argsort(idx).astype(NP_TYPES.INT)

    # sort data
    material = material[idx_sort]

    # assign the data to the geometry
    voxel["material"] = material

    return voxel


def set_plotter_voxel_scalar(voxel, idx, idx_var, var, name):
    """
    Add a scalar variable to the unstructured grid (complex variable).
    """

    # find the variable indices
    idx_s = np.argsort(idx).astype(NP_TYPES.INT)
    idx_p = np.searchsorted(idx, idx_var, sorter=idx_s).astype(NP_TYPES.INT)
    idx_var_local = idx_s[idx_p]

    # assign scalar variable (nan for the voxels where the variable is not defined)
    var_all = np.full(len(idx), np.nan+1j*np.nan, dtype=NP_TYPES.COMPLEX)
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
    idx_s = np.argsort(idx).astype(NP_TYPES.INT)
    idx_p = np.searchsorted(idx, idx_var, sorter=idx_s).astype(NP_TYPES.INT)
    idx_var_local = idx_s[idx_p]

    # assign vector variable (nan for the voxels where the variable is not defined)
    var_all = np.full((len(idx), 3), np.nan+1j*np.nan, dtype=NP_TYPES.COMPLEX)
    var_all[idx_var_local] = var

    # sort the variable
    var_all = var_all[idx_s]

    # assign the vector and the norm
    voxel[name + "_vec_re"] = np.real(var_all)
    voxel[name + "_vec_im"] = np.imag(var_all)
    voxel[name + "_norm"] = lna.norm(var_all, axis=1)

    return voxel


def set_plotter_magnetic_field(point, H_point):
    """
    Add the magnetic field to the point cloud.
    The norm (scalar field) and the direction (vector field) are added.
    """

    # assign the vector and the norm
    point["H_vec_re"] = np.real(H_point)
    point["H_vec_im"] = np.imag(H_point)
    point["H_norm"] = lna.norm(H_point, axis=1)

    return point
