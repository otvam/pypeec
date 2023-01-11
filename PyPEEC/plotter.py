"""
Main script for plotting the solution of a FFT-PEEC problem.
Plot the material description, the resistivity, the potential, and the current density.

The plotting is done with PyVista with the Qt framework.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import os
import qtpy.QtWidgets as qtw
import qtpy.QtGui as qtu
import pyvistaqt as pvqt
from PyPEEC.lib_plotter import check_data
from PyPEEC.lib_plotter import manage_voxel
from PyPEEC.lib_plotter import manage_plot
from PyPEEC.lib_shared import logging_utils

# get a logger
logger = logging_utils.get_logger("plotter")


def _run_check(data_plotter):
    """
    Check the input data.
    Exceptions are not caught inside this function.
    """

    # check the data type
    check_data.check_data_plotter(data_plotter)

    # check the plot
    for dat_tmp in data_plotter:
        check_data.check_plotter_item(dat_tmp)


def _get_grid_voxel(data_res):
    """
    Convert the complete voxel geometry into a PyVista uniform grid.
    Convert the non-empty voxel geometry into a PyVista unstructured grid.
    Add the solver results (material description, resistivity, and field) to the grid.
    """

    # extract the data
    n = data_res["n"]
    d = data_res["d"]
    idx_v = data_res["idx_v"]
    idx_src_c = data_res["idx_src_c"]
    idx_src_v = data_res["idx_src_v"]
    rho_v = data_res["rho_v"]
    V_v = data_res["V_v"]
    J_v = data_res["J_v"]

    # convert the voxel geometry into PyVista grids
    (grid, geom) = manage_voxel.get_grid_geom(n, d, idx_v)

    # add the problem solution to the grid
    geom = manage_voxel.get_material(geom, idx_v, idx_src_c, idx_src_v)
    geom = manage_voxel.get_resistivity(geom, idx_v, rho_v)
    geom = manage_voxel.get_potential(geom, idx_v, V_v)
    geom = manage_voxel.get_current_density(geom, idx_v, J_v)

    return grid, geom


def _get_plot(grid, geom, data_plotter):
    """
    Make a plot with the specified user settings.
    The plot contains the following elements:
        - the geometry as wireframe
        - the axis, color bar, and legend
        - the payload (material description, scalar plots, or arrow plots)
    """

    # extract the data
    window_title = data_plotter["window_title"]
    window_size = data_plotter["window_size"]
    plot_type = data_plotter["plot_type"]
    data_options = data_plotter["data_options"]
    plot_options = data_plotter["plot_options"]

    # get the plotter (with the Qt framework)
    pl = pvqt.BackgroundPlotter(
        toolbar=False,
        menu_bar=False,
        title=window_title,
        window_size=window_size
    )

    # set icon
    path = os.path.dirname(__file__)
    filename = os.path.join(path, "icon.png")
    pl.app.setWindowIcon(qtu.QIcon(filename))

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
    logger.info("init")

    # check the input data
    logger.info("check the input data")
    try:
        _run_check(data_plotter)
    except check_data.CheckError as ex:
        logger.error(str(ex))
        return False

    # create the Qt app (should be at the beginning)
    logger.info("create the GUI application")
    app = qtw.QApplication([])

    # handle the data
    logger.info("parse the voxel geometry and the data")
    (grid, geom) = _get_grid_voxel(data_res)

    # make the plots
    logger.info("generate the different plots")
    for i, dat_tmp in enumerate(data_plotter):
        logger.info("plotting %d / %d" % (i+1, len(data_plotter)))
        _get_plot(grid, geom, dat_tmp)

    # end message
    logger.info("successful termination")

    # enter the event loop (should be at the end, blocking call)
    return app.exec_()
