"""
Different functions for extracting PyVista grids from the voxel structure.
Add the solution (material description, resistivity, potential, and current density) to the PyVista grids.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np
import numpy.linalg as lna
import pyvista as pv


def get_grid_geom(n, d, ori, idx_voxel):
    """
    Construct PyVista grids from the voxel structure.
    The complete voxel geometry is represented with a PyVista uniform grid.
    The non-empty voxel geometry is represented with a PyVista unstructured grid.
    """

    # extract the voxel data_output
    (nx, ny, nz) = n
    (dx, dy, dz) = d
    (orix, oriy, oriz) = ori

    # create a uniform grid for the complete structure
    grid = pv.UniformGrid()

    # set the array size and the voxel size
    grid.dimensions = (nx+1, ny+1, nz+1)
    grid.spacing = (dx, dy, dz)  # These are the cell sizes along each axis
    grid.origin = (orix, oriy, oriz)

    # get voxel indices
    idx = np.flatnonzero(idx_voxel)

    # transform the uniform grid into a unstructured grid (keeping the non-empty voxels)
    geom = grid.extract_cells(idx)

    return grid, geom


def get_material(idx_voxel, geom, conductor, source):
    """
    Extract and add to the geometry the material description.
    The following encoding is used:
        - 0: conducting voxels
        - 1: current source voxels
        - 2: voltage source voxels
    """

    # assign empty data_output
    data = np.full(len(idx_voxel), np.nan, dtype=np.float64)

    # assign conductor voxels
    for tag, dat_tmp in conductor.items():
        # get the data_output
        idx_tmp = dat_tmp["idx"]

        # assign the material
        data[idx_tmp] = 0

    # assign source voxels
    for tag, dat_tmp in source.items():
        # get the data_output
        idx_tmp = dat_tmp["idx"]
        source_type_tmp = dat_tmp["source_type"]

        # assign the material (current or voltage sources)
        if source_type_tmp == "current":
            data[idx_tmp] = 1
        elif source_type_tmp == "voltage":
            data[idx_tmp] = 2
        else:
            raise ValueError("invalid terminal type")

    # get voxel indices
    idx = np.flatnonzero(idx_voxel)

    # assign the extract data_output to the geometry
    geom["material"] = data[idx]

    return geom


def get_resistivity(idx_voxel, geom, rho_voxel):
    """
    Extract and add to the geometry the resistivity.
    """

    # get voxel indices
    idx = np.flatnonzero(idx_voxel)
    rho = rho_voxel[idx]

    # assign the extract data_output to the geometry
    geom["rho"] = rho

    return geom


def get_potential(idx_voxel, geom, V_voxel):
    """
    Extract and add to the geometry the potential (solved variable).
    Assign the real part, the imaginary part, and the absolute value.
    """

    # get voxel indices
    idx = np.flatnonzero(idx_voxel)
    V = V_voxel[idx]

    # assign the extract data_output to the geometry
    geom["V_re"] = np.real(V)
    geom["V_im"] = np.imag(V)
    geom["V_abs"] = np.abs(V)

    return geom


def get_current_density(idx_voxel, geom, J_voxel):
    """
    Extract and add to the geometry the current density (solved variable).
    Assign the real part and the imaginary part for the current density vector.
    Assign the real part, the imaginary part, and the absolute value for the current density norm.
    """

    # get voxel indices
    idx = np.flatnonzero(idx_voxel)
    J = J_voxel[idx, :]

    # assign the extract data_output to the geometry
    geom["J_norm_abs"] = lna.norm(J, axis=1)
    geom["J_norm_re"] = lna.norm(np.real(J), axis=1)
    geom["J_norm_im"] = lna.norm(np.imag(J), axis=1)
    geom["J_vec_re"] = np.real(J)
    geom["J_vec_im"] = np.imag(J)

    return geom
