"""
Different functions for extracting PyVista object from the voxel structure:
    - The complete voxel structure (uniform grid).
    - The structure containing non-empty voxels (unstructured grid).
    - The defined point cloud (polydata object).
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import vtk
import numpy as np
import pyvista as pv

# prevent VTK to mess up the output
vtk.vtkObject.GlobalWarningDisplayOff()


def get_grid(n, d, c):
    """
    Construct a PyVista uniform grid for the complete voxel structure.
    """

    # extract the voxel data
    (nx, ny, nz) = n
    (dx, dy, dz) = d
    (cx, cy, cz) = c

    # origin coordinate
    ox = cx - (nx * dx) / 2
    oy = cy - (ny * dy) / 2
    oz = cz - (nz * dz) / 2

    # create a uniform grid for the complete structure
    grid = pv.ImageData()

    # set the array size and the voxel size
    grid.origin = (ox, oy, oz)
    grid.dimensions = (nx + 1, ny + 1, nz + 1)
    grid.spacing = (dx, dy, dz)

    return grid


def get_voxel(grid, idx):
    """
    Construct a PyVista unstructured grid for the non-empty voxels.
    The indices of the non-empty voxels are provided.
    """

    # assemble idx
    idx = np.sort(idx)

    # transform the uniform grid into an unstructured grid (keeping the non-empty voxels)
    voxel = grid.extract_cells(idx)

    return voxel


def get_point(pts_cloud):
    """
    Construct a PyVista point cloud (polydata) with the defined points.
    """

    point = pv.PolyData(pts_cloud)

    return point


def get_reference(geom_def):
    """
    Construct a PyVista object from the reference mesh.
    """

    # create an empty mesh
    reference = pv.PolyData()

    # add the different reference meshes
    for geom_tmp in geom_def:
        reference += pv.PolyData(
            geom_tmp["points"],
            lines=geom_tmp["lines"],
            faces=geom_tmp["faces"],
        )

    return reference
