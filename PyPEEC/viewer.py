"""
Main script for visualizing a 3D voxel structure.
Plot the geometry and color the different domains.

The plotting is done with PyVista with the Qt framework.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import os
import pyvistaqt as pvqt
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import QApplication
from PyPEEC.lib_viewer import manage_voxel
from PyPEEC.lib_viewer import manage_plot
from PyPEEC.lib_shared import logging_utils
from PyPEEC.lib_shared import check_data_viewer
from PyPEEC.lib_shared import check_data_voxel
from PyPEEC.error import CheckError, RunError

# get a logger
logger = logging_utils.get_logger("viewer")


def _run_check(data_voxel, data_viewer):
    """
    Check the input data.
    Exceptions are not caught inside this function.
    """

    # check the viewer data
    check_data_voxel.check_data_voxel(data_voxel)

    # check the viewer data
    check_data_viewer.check_data_viewer(data_viewer)


def _get_grid_voxel(data_res):
    """
    Convert the complete voxel geometry into a PyVista uniform grid.
    Convert the non-empty voxel geometry into a PyVista unstructured grid.
    Add the domain tags to the grid.
    """

    # extract the data
    n = data_res["n"]
    d = data_res["d"]
    domain_def = data_res["domain_def"]

    # convert the voxel geometry into a PyVista uniform grid
    grid = manage_voxel.get_grid(n, d)

    # convert the voxel geometry into a PyVista unstructured grid
    geom = manage_voxel.get_geom(grid, domain_def)

    return grid, geom


def _get_plot(grid, geom, data_viewer):
    """
    Make a plot with the voxel structure and the domains.
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
    pl.app.setWindowIcon(QIcon(filename))

    # find the plot type and call the corresponding function
    manage_plot.get_plot_domain(pl, geom)
    manage_plot.get_plot_base(pl, grid, geom, plot_title, plot_options)


def run(data_voxel, data_viewer):
    """
    Main script for visualizing a 3D voxel structure.
    """

    # init
    logger.info("init")

    # run the code
    try:
        # check the input data
        logger.info("check the input data")
        _run_check(data_voxel, data_viewer)

        # create the Qt app (should be at the beginning)
        logger.info("create the GUI application")
        app = QApplication([])

        # handle the data
        logger.info("parse the voxel geometry and the data")
        (grid, geom) = _get_grid_voxel(data_voxel)

        # make the plots
        logger.info("generate the plot")
        _get_plot(grid, geom, data_viewer)
    except CheckError as ex:
        logger.error("check error : " + str(ex))
        return False
    except RunError as ex:
        logger.error("check error : " + str(ex))
        return False

    # end message
    logger.info("successful termination")

    # enter the event loop (should be at the end, blocking call)
    return app.exec_()
