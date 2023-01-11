"""
Different functions for extracting PyVista grids from the voxel structure.
Add the domain tags to the grid as a fake scalar field.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np
import pyvista as pv


def get_grid(n, d):
    """
    Construct a PyVista grid from the voxel structure.
    The complete voxel geometry is represented with a PyVista uniform grid.
    """

    # extract the voxel data
    (nx, ny, nz) = n
    (dx, dy, dz) = d

    # create a uniform grid for the complete structure
    grid = pv.UniformGrid()

    # set the array size and the voxel size
    grid.dimensions = (nx+1, ny+1, nz+1)
    grid.spacing = (dx, dy, dz)  # These are the cell sizes along each axis
    grid.origin = (0, 0, 0)

    return grid


def get_geom(grid, domain_def):
    """
    Construct a PyVista grid from the voxel structure.
    The non-empty voxel geometry is represented with a PyVista unstructured grid.
    Add the domain tags to the grid as a fake scalar field.
    """

    # init
    idx_domain = np.array([], dtype=np.int64)
    color_domain = np.array([], dtype=np.int64)

    # get the indices and colord
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

    # transform the uniform grid into a unstructured grid (keeping the non-empty voxels)
    geom = grid.extract_cells(idx_domain)

    # assign the colord
    geom["domain"] = color_domain

    return geom
