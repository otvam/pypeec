from plotter import manage_voxel
from plotter import manage_plot
from main import logging_utils

# get a logger
logger = logging_utils.get_logger("plotter", "INFO")


def __extract_voxel(data_res):
    """
    Convert the voxel geometry into an unstructured grid.
    Add the solver results (field, material, resistivity) to the grid.
    """

    n = data_res["n"]
    d = data_res["d"]
    ori = data_res["ori"]
    idx_voxel = data_res["idx_voxel"]
    rho_voxel = data_res["rho_voxel"]
    V_voxel = data_res["V_voxel"]
    J_voxel = data_res["J_voxel"]
    src_terminal = data_res["src_terminal"]

    # convert the voxel geometry into a unstructured grid.
    (grid, geom) = manage_voxel.get_geom(n, d, ori, idx_voxel)

    # add the solution to the grid
    geom = manage_voxel.get_material(idx_voxel, geom, src_terminal)
    geom = manage_voxel.get_resistivity(idx_voxel, geom, rho_voxel)
    geom = manage_voxel.get_potential(idx_voxel, geom, V_voxel)
    geom = manage_voxel.get_current_density(idx_voxel, geom, J_voxel)

    return grid, geom


def run(data_res, data_plotter):
    # init
    logger.info("INIT")

    logger.info("parse the voxel geometry and the data")
    (grid, geom) = __extract_voxel(data_res)

    # end
    logger.info("END")