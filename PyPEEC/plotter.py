"""
Main script for plotting the solution of a FFT-PEEC problem.
Plot the material description, the resistivity, the potential, and the current density.

The plotting is done with PyVista with the Qt framework.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import qtpy.QtWidgets as qtw
import pyvistaqt as pvqt
from PyPEEC.lib_plotter import manage_voxel
from PyPEEC.lib_plotter import manage_plot
from PyPEEC.lib_shared import logging_utils

# get a logger
logger = logging_utils.get_logger("lib_plotter")


def _get_grid_voxel(data_res):
    """
    Convert the complete voxel geometry into a PyVista uniform grid.
    Convert the non-empty voxel geometry into a PyVista unstructured grid.
    Add the lib_solver results (material description, resistivity, and field) to the grid.
    """

    # extract the data_output
    n = data_res["n"]
    d = data_res["d"]
    ori = data_res["ori"]
    idx_voxel = data_res["idx_voxel"]
    rho_voxel = data_res["rho_voxel"]
    V_voxel = data_res["V_voxel"]
    J_voxel = data_res["J_voxel"]
    source = data_res["source"]
    conductor = data_res["conductor"]

    # convert the voxel geometry into PyVista grids
    (grid, geom) = manage_voxel.get_grid_geom(n, d, ori, idx_voxel)

    # add the problem solution to the grid
    geom = manage_voxel.get_material(idx_voxel, geom, conductor, source)
    geom = manage_voxel.get_resistivity(idx_voxel, geom, rho_voxel)
    geom = manage_voxel.get_potential(idx_voxel, geom, V_voxel)
    geom = manage_voxel.get_current_density(idx_voxel, geom, J_voxel)

    return grid, geom


def _get_plot(grid, geom, data_plotter):
    """
    Make a plot with the specified user settings.
    The plot contains the following elements:
        - the geometry as wireframe
        - the axis, color bar, and legend
        - the payload (material description, scalar plots, or arrow plots)
    """

    # extract the data_output
    title = data_plotter["title"]
    window_size = data_plotter["window_size"]
    plot_type = data_plotter["plot_type"]
    data_options = data_plotter["data_options"]
    plot_options = data_plotter["plot_options"]

    # get the lib_plotter (with the Qt framework)
    pl = pvqt.BackgroundPlotter(
        toolbar=False,
        menu_bar=False,
        title=title,
        window_size=window_size
    )

    # find the plot type and call the corresponding function
    if plot_type == "material":
        manage_plot.plot_material(pl, grid, geom, plot_options, data_options)
    elif plot_type == "scalar":
        manage_plot.plot_scalar(pl, grid, geom, plot_options, data_options)
    elif plot_type == "arrow":
        manage_plot.plot_arrow(pl, grid, geom, plot_options, data_options)
    else:
        raise ValueError("invalid plot type")


def run(data_res, data_plotter):
    """
    Main script for plotting the solution of a FFT-PEEC problem.
    """

    # init
    logger.info("INIT")

    # create the Qt app (should be at the beginning)
    logger.info("create the GUI application")
    app = qtw.QApplication([])

    # handle the data_output
    logger.info("parse the voxel geometry and the data_output")
    (grid, geom) = _get_grid_voxel(data_res)

    # make the plots
    logger.info("generate the different plots")
    for i, dat_tmp in enumerate(data_plotter):
        logger.info("plotting %d / %d" % (i+1, len(data_plotter)))
        _get_plot(grid, geom, dat_tmp)

    # end
    logger.info("END")

    # enter the event loop (should be at the end, blocking call)
    return app.exec_()
