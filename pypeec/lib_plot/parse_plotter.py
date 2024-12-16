"""
Add data to the PyVista objects for the plotter:
    - scalar variables
    - vector variables
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import numpy as np
import numpy.linalg as lna


def set_voxel_material(voxel, idx, idx_vc, idx_vm, idx_src_c, idx_src_v):
    """
    Add the material and source description to the unstructured grid.
    Integers are used to encode the different tags.
    """

    # find position
    idx_vc_local = np.isin(idx, idx_vc)
    idx_vm_local = np.isin(idx, idx_vm)
    idx_src_c_local = np.isin(idx, idx_src_c)
    idx_src_v_local = np.isin(idx, idx_src_v)
    idx_vcm_local = np.logical_and(idx_vc_local, idx_vm_local)

    # init the material
    material = np.empty(len(idx), dtype=np.int64)

    # assign the materials
    material[idx_vc_local] = 1
    material[idx_vm_local] = 2
    material[idx_vcm_local] = 3

    # assign the sources
    material[idx_src_c_local] = 4
    material[idx_src_v_local] = 5

    # get sorted indices
    idx_sort = np.argsort(idx)

    # sort data
    material = material[idx_sort]

    # assign the data to the geometry
    voxel["material"] = material

    return voxel


def set_voxel_scalar(voxel, idx, idx_var, var, name):
    """
    Add a scalar variable to the unstructured grid (complex variable).
    """

    # find the variable indices
    idx_s = np.argsort(idx)
    idx_p = np.searchsorted(idx, idx_var, sorter=idx_s)
    idx_var_local = idx_s[idx_p]

    # assign scalar variable (nan for the voxels where the variable is not defined)
    var_all = np.full(len(idx), np.nan + 1j * np.nan, dtype=np.complex128)
    var_all[idx_var_local] = var

    # sort the variable
    var_all = var_all[idx_s]

    # assign potential
    voxel[name + "_re"] = np.real(var_all)
    voxel[name + "_im"] = np.imag(var_all)
    voxel[name + "_norm"] = np.abs(var_all)

    return voxel


def set_voxel_vector(voxel, idx, idx_var, var, name):
    """
    Add a vector variable to the unstructured grid (complex variable).
    The norm (scalar field) and the direction (vector field) are added.
    """

    # find the variable indices
    idx_s = np.argsort(idx)
    idx_p = np.searchsorted(idx, idx_var, sorter=idx_s)
    idx_var_local = idx_s[idx_p]

    # assign vector variable (nan for the voxels where the variable is not defined)
    var_all = np.full((len(idx), 3), np.nan + 1j * np.nan, dtype=np.complex128)
    var_all[idx_var_local] = var

    # sort the variable
    var_all = var_all[idx_s]

    # assign the vector and the norm
    voxel[name + "_re"] = np.real(var_all)
    voxel[name + "_im"] = np.imag(var_all)
    voxel[name + "_norm"] = lna.norm(var_all, axis=1)

    return voxel


def set_point_cloud(point, var, name):
    """
    Add a vector variable defined on the point cloud.
    The norm (scalar field) and the direction (vector field) are added.
    """

    # assign the vector and the norm
    point[name + "_re"] = np.real(var)
    point[name + "_im"] = np.imag(var)
    point[name + "_norm"] = lna.norm(var, axis=1)

    return point


def get_voxel(idx_vc, idx_vm):
    """
    Get the indices of the non-empty voxels.
    """

    idx_all = np.concatenate((idx_vc, idx_vm))
    idx_all = np.unique(idx_all)

    return idx_all
