"""
Different functions for extracting PyVista grids from the voxel structure.
Add the solution (material description, resistivity, potential, and current density) to the PyVista grids.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np
import numpy.linalg as lna
import pyvista as pv


def get_grid_geom(n, d, ori, idx_v):
    """
    Construct PyVista grids from the voxel structure.
    The complete voxel geometry is represented with a PyVista uniform grid.
    The non-empty voxel geometry is represented with a PyVista unstructured grid.
    """

    # extract the voxel data
    (nx, ny, nz) = n
    (dx, dy, dz) = d
    (orix, oriy, oriz) = ori

    # create a uniform grid for the complete structure
    grid = pv.UniformGrid()

    # set the array size and the voxel size
    grid.dimensions = (nx+1, ny+1, nz+1)
    grid.spacing = (dx, dy, dz)  # These are the cell sizes along each axis
    grid.origin = (orix, oriy, oriz)

    # transform the uniform grid into a unstructured grid (keeping the non-empty voxels)
    geom = grid.extract_cells(idx_v)

    return grid, geom


def get_material(geom, idx_v, idx_src_c, idx_src_v):
    """
    Extract and add to the geometry the material description.
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

    # assign the extract data to the geometry
    geom["material"] = data

    return geom


def get_resistivity(geom, idx_v, rho_v):
    """
    Extract and add to the geometry the resistivity.
    """

    # sort idx
    idx = np.argsort(idx_v)
    rho_v = rho_v[idx]

    # assign data
    geom["rho"] = rho_v

    return geom


def get_potential(geom, idx_v, V_v):
    """
    Extract and add to the geometry the potential (solved variable).
    Assign the real part, the imaginary part, and the absolute value.
    """

    # sort idx
    idx = np.argsort(idx_v)
    V_v = V_v[idx]

    # assign data
    geom["V_re"] = np.real(V_v)
    geom["V_im"] = np.imag(V_v)
    geom["V_abs"] = np.abs(V_v)

    return geom


def get_current_density(geom, idx_v, J_v):
    """
    Extract and add to the geometry the current density (solved variable).
    Assign the real part and the imaginary part for the current density vector.
    Assign the real part, the imaginary part, and the absolute value for the current density norm.
    """

    # sort idx
    idx = np.argsort(idx_v)
    J_v = J_v[idx, :]

    # compute the norm
    geom["J_norm_abs"] = lna.norm(J_v, axis=1)
    geom["J_norm_re"] = lna.norm(np.real(J_v), axis=1)
    geom["J_norm_im"] = lna.norm(np.imag(J_v), axis=1)

    # compute the direction, ignore division per zero
    with np.errstate(all="ignore"):
        geom["J_vec_unit_re"] = np.real(J_v)/lna.norm(np.real(J_v), axis=1, keepdims=True)
        geom["J_vec_unit_im"] = np.imag(J_v)/lna.norm(np.imag(J_v), axis=1, keepdims=True)

    return geom
