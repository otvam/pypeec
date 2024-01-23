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
    idx_vc_local = np.in1d(idx, idx_vc)
    idx_vm_local = np.in1d(idx, idx_vm)
    idx_src_c_local = np.in1d(idx, idx_src_c)
    idx_src_v_local = np.in1d(idx, idx_src_v)

    # init the material
    material = np.empty(len(idx), dtype=np.int_)

    # assign the voltage and current sources
    material[idx_vc_local] = 1
    material[idx_vm_local] = 2
    material[idx_src_c_local] = 3
    material[idx_src_v_local] = 4

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
    var_all = np.full(len(idx), np.nan+1j*np.nan, dtype=np.complex_)
    var_all[idx_var_local] = var

    # sort the variable
    var_all = var_all[idx_s]

    # assign potential
    voxel[name + "_re"] = np.real(var_all)
    voxel[name + "_im"] = np.imag(var_all)
    voxel[name + "_abs"] = np.abs(var_all)

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
    var_all = np.full((len(idx), 3), np.nan+1j*np.nan, dtype=np.complex_)
    var_all[idx_var_local] = var

    # sort the variable
    var_all = var_all[idx_s]

    # assign the vector and the norm
    voxel[name + "_vec_re"] = np.real(var_all)
    voxel[name + "_vec_im"] = np.imag(var_all)
    voxel[name + "_norm"] = lna.norm(var_all, axis=1)

    return voxel


def set_magnetic_field(point, H_pts):
    """
    Add the magnetic field to the point cloud.
    The norm (scalar field) and the direction (vector field) are added.
    """

    # assign the vector and the norm
    point["H_vec_re"] = np.real(H_pts)
    point["H_vec_im"] = np.imag(H_pts)
    point["H_norm"] = lna.norm(H_pts, axis=1)

    return point


def get_voxel(idx_vc, idx_vm):
    """
    Get the indices of the non-empty voxels.
    """

    idx_all = np.concatenate((idx_vc, idx_vm))

    return idx_all
