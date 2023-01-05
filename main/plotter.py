import qtpy.QtWidgets as qtw
import pyvistaqt as pvqt

from plotter import manage_voxel
from plotter import manage_plot
from main import logging_utils


# get a logger
logger = logging_utils.get_logger("plotter", "INFO")


def __get_grid_voxel(data_res):
    """
    Convert the voxel geometry into an unstructured grid.
    Add the solver results (field, material, resistivity) to the grid.
    """

    # extract the data
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


def __get_plot(grid, geom, data_plotter):
    # extract the data
    title = data_plotter["title"]
    window_size = data_plotter["window_size"]
    plot_type = data_plotter["plot_type"]
    data_options = data_plotter["data_options"]
    plot_options = data_plotter["plot_options"]

    # get the plotter
    pl = pvqt.BackgroundPlotter(
        toolbar=False,
        menu_bar=False,
        title=title,
        window_size=window_size
    )

    # find the plot type
    if plot_type == "material":
        manage_plot.plot_material(pl, grid, geom, plot_options, data_options)
    elif plot_type == "scalar":
        manage_plot.plot_scalar(pl, grid, geom, plot_options, data_options)
    elif plot_type == "arrow":
        manage_plot.plot_arrow(pl, grid, geom, plot_options, data_options)
    else:
        raise ValueError("invalid plot type")


def run(data_res, data_plotter):
    # init
    logger.info("INIT")

    # create the Qt app (should be at the beginning)
    logger.info("parse the voxel geometry and the data")
    app = qtw.QApplication([])

    # handle the data
    logger.info("parse the voxel geometry and the data")
    (grid, geom) = __get_grid_voxel(data_res)

    # make the plots
    logger.info("parse the voxel geometry and the data")
    for dat_tmp in data_plotter:
        __get_plot(grid, geom, dat_tmp)

    # end
    logger.info("END")

    # enter the event loop (should be at the end)
    return app.exec_()
