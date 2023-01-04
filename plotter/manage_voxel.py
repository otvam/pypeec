import numpy as np
import pyvista as pv


def get_geom(n, d, ori, idx_voxel):
    # extract the voxel data
    (nx, ny, nz) = n
    (dx, dy, dz) = d
    (orix, oriy, oriz) = ori

    # create a uniform grid for the complete structure
    grid = pv.UniformGrid()

    # set the array size
    grid.dimensions = (nx+1, ny+1, nz+1)
    grid.spacing = (dx, dy, dz)  # These are the cell sizes along each axis
    grid.origin = (orix-dx/2, oriy-dy/2, oriz-dz/2)

    # get voxel indices
    idx = np.flatnonzero(idx_voxel)
    geom = grid.extract_cells(idx)

    return grid, geom


def get_material(idx_voxel, geom, src_terminal):
    # assign empty data
    data = np.full(len(idx_voxel), np.nan, dtype=np.float64)

    # assign conductor
    idx = np.flatnonzero(idx_voxel)
    data[idx] = 0

    # assign terminal
    for tag in src_terminal:
        # get the data
        idx_tmp = src_terminal[tag]["idx"]
        type_tmp = src_terminal[tag]["type"]

        # assign the material
        if type_tmp == "current":
            data[idx_tmp] = 1
        elif type_tmp == "voltage":
            data[idx_tmp] = 2
        else:
            raise ValueError("invalid terminal type")

    # assign the material to the dataset
    geom["material"] = data[idx]

    return geom


def get_resistivity(idx_voxel, geom, rho_voxel):
    # assign resistivity
    idx = np.flatnonzero(idx_voxel)
    geom["rho"] = rho_voxel[idx]

    return geom




    return geom