from plotter import manage_voxel
from plotter import manage_plot
from main import logging_utils

# get a logger
logger = logging_utils.get_logger("plotter", "INFO")


def __extract_voxel():
    n = data_res["n"]
    d = data_res["d"]
    ori = data_res["ori"]
    idx_voxel = data_res["idx_voxel"]
    rho_voxel = data_res["rho_voxel"]
    V_voxel = data_res["V_voxel"]
    J_voxel = data_res["J_voxel"]
    src_terminal = data_res["src_terminal"]

    plot_options = {
        "grid_plot": True,
        "grid_thickness": 1.0,
        "grid_opacity": 0.1,
        "geom_plot": True,
        "geom_thickness": 1.0,
        "geom_opacity": 0.5,
    }

    (grid, geom) = manage_voxel.get_geom(n, d, ori, idx_voxel)
    geom = manage_voxel.get_material(idx_voxel, geom, src_terminal)
    geom = manage_voxel.get_resistivity(idx_voxel, geom, rho_voxel)
    geom = manage_voxel.get_potential(idx_voxel, geom, V_voxel)
    geom = manage_voxel.get_current_density(idx_voxel, geom, J_voxel)


def run(data_res, data_plotter):
    # init
    logger.info("INIT")

    # end
    logger.info("END")