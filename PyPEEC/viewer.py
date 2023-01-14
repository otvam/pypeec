"""
Main script for visualizing a 3D voxel structure.
Plot the geometry and color the different domains.

The plotting is done with PyVista with the Qt framework.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

from PyPEEC.lib_viewer import manage_voxel
from PyPEEC.lib_viewer import manage_plot
from PyPEEC.lib_shared import check_data_viewer
from PyPEEC.lib_shared import check_data_voxel
from PyPEEC.lib_utils import vistagui
from PyPEEC.lib_utils import timelogger
from PyPEEC.lib_utils.error import CheckError, RunError

# get a logger
logger = timelogger.get_logger("viewer")


def _get_grid_voxel(data_voxel):
    """
    Convert the complete voxel geometry into a PyVista uniform grid.
    Convert the non-empty voxel geometry into a PyVista unstructured grid.
    Add the domain tags to the grid.
    """

    # extract the data
    n = data_voxel["n"]
    d = data_voxel["d"]
    domain_def = data_voxel["domain_def"]

    # convert the voxel geometry into a PyVista uniform grid
    grid = manage_voxel.get_grid(n, d)

    # convert the voxel geometry into a PyVista unstructured grid
    geom = manage_voxel.get_geom(grid, domain_def)

    return grid, geom


def _get_plot(grid, geom, data_viewer, is_blocking):
    """
    Make a plot with the voxel structure and the domains.
    """

    # extract the data
    plot_title = data_viewer["plot_title"]
    data_window = data_viewer["data_window"]
    plot_options = data_viewer["plot_options"]

    # get the plotter (with the Qt framework)
    pl = vistagui.open_plotter(data_window, is_blocking)

    # find the plot type and call the corresponding function
    manage_plot.get_plot_domain(pl, geom)
    manage_plot.get_plot_base(pl, grid, geom, plot_title, plot_options)

    # close plotter is non blocking
    vistagui.close_plotter(pl, is_blocking)


def run(data_voxel, data_viewer, is_blocking):
    """
    Main script for visualizing a 3D voxel structure.
    """

    # init
    logger.info("init")

    # run the code
    try:
        # check the input data
        logger.info("check the input data")
        check_data_voxel.check_data_voxel(data_voxel)
        check_data_viewer.check_data_viewer(data_viewer)

        # create the Qt app (should be at the beginning)
        logger.info("create the GUI application")
        app = vistagui.open_app(is_blocking)

        # handle the data
        logger.info("parse the voxel geometry and the data")
        (grid, geom) = _get_grid_voxel(data_voxel)

        # make the plots
        logger.info("generate the plot")
        _get_plot(grid, geom, data_viewer, is_blocking)
    except CheckError as ex:
        logger.error("check error : " + str(ex))
        return False
    except RunError as ex:
        logger.error("check error : " + str(ex))
        return False

    # end message
    logger.info("successful termination")

    # enter the event loop (should be at the end, blocking call)
    return vistagui.run_app(app, is_blocking)
