"""
Different functions for extracting PyVista grids from the voxel structure.
Add the domain tags to the grid as a fake scalar field.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np
from PyPEEC.lib_shared import plot_geometry


def get_grid_geom(n, d, domain_def):
    """
    Construct a PyVista unstructured grid for the non-empty voxel.
    Add the domain tags to the grid as a fake scalar field.
    """

    # get the regular grid
    grid = plot_geometry.get_grid(n, d)

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

    # transform the uniform grid into an unstructured grid (keeping the non-empty voxels)
    geom = grid.extract_cells(idx_domain)

    # assign the colord
    geom["domain"] = color_domain

    return grid, geom
