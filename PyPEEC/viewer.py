"""
Main script for visualizing a 3D voxel structure.
Plot the geometry and the different domains.

The plotting is done with PyVista with the Qt framework.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import os
import qtpy.QtWidgets as qtw
import qtpy.QtGui as qtu
import pyvistaqt as pvqt
from PyPEEC.lib_viewer import check_data
from PyPEEC.lib_viewer import manage_voxel
from PyPEEC.lib_viewer import manage_plot
from PyPEEC.lib_shared import logging_utils

# get a logger
logger = logging_utils.get_logger("viewer")


def _run_check(data_voxel, data_viewer):
    """
    Check the input data.
    Exceptions are not caught inside this function.
    """

    # check the viewer data
    check_data.check_voxel(data_voxel)

    # check the viewer data
    check_data.check_viewer(data_viewer)


def _get_grid_voxel(data_res):
    """
    Convert the complete voxel geometry into a PyVista uniform grid.
    Convert the non-empty voxel geometry into a PyVista unstructured grid.
    Add the domain tags to the grid.
    """

    # extract the data
    n = data_res["n"]
    d = data_res["d"]
    ori = data_res["ori"]
    domain_def = data_res["domain_def"]

    # convert the voxel geometry into a PyVista uniform grid
    grid = manage_voxel.get_grid(n, d, ori)

    # convert the voxel geometry into a PyVista unstructured grid
    geom = manage_voxel.get_geom(grid, domain_def)

    return grid, geom


def _get_plot(grid, geom, data_viewer):
    """
    Make a plot with the voxel structure.
    """

    # extract the data
    window_title = data_viewer["window_title"]
    plot_title = data_viewer["plot_title"]
    window_size = data_viewer["window_size"]
    plot_options = data_viewer["plot_options"]

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
    manage_plot.get_plot_domain(pl, geom)
    manage_plot.get_plot_base(pl, grid, geom, plot_title, plot_options)

def run(data_voxel, data_viewer):
    """
    Main script for visualizing a 3D voxel structure.
    """

    # init
    logger.info("init")

    # check the input data
    logger.info("check the input data")
    try:
        _run_check(data_voxel, data_viewer)
    except check_data.CheckError as ex:
        logger.error(str(ex))
        return False

    # create the Qt app (should be at the beginning)
    logger.info("create the GUI application")
    app = qtw.QApplication([])

    # handle the data
    logger.info("parse the voxel geometry and the data")
    (grid, geom) = _get_grid_voxel(data_voxel)

    # make the plots
    logger.info("generate the plot")
    _get_plot(grid, geom, data_viewer)

    # end message
    logger.info("successful termination")

    # enter the event loop (should be at the end, blocking call)
    return app.exec_()
