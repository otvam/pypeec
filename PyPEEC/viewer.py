"""
Main script for visualizing a 3D voxel structure.
Plot the following features:
    - the different domain composing the voxel structure
    - the connected components of the voxel structure

The plotting is done with PyVista with the Qt framework.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

from PyPEEC.lib_visualization import manage_voxel
from PyPEEC.lib_visualization import manage_plot
from PyPEEC.lib_check import check_data_point
from PyPEEC.lib_check import check_data_visualization
from PyPEEC.lib_utils import vistagui
from PyPEEC.lib_utils import timelogger
from PyPEEC.lib_utils.error import CheckError, RunError

# get a logger
logger = timelogger.get_logger("viewer")


def _get_grid_voxel(data_voxel, data_point):
    """
    Convert the complete voxel geometry into a PyVista uniform grid.
    Convert the non-empty voxel geometry into a PyVista unstructured grid.
    Add the domain tags to the grid.
    """

    # extract the data
    n = data_voxel["n"]
    d = data_voxel["d"]
    c = data_voxel["c"]
    domain_def = data_voxel["domain_def"]
    graph_def = data_voxel["graph_def"]

    # get the indices of the non-empty voxels
    (idx_v, dom_v, gra_v) = manage_voxel.get_viewer_domain(domain_def, graph_def)

    # convert the voxel geometry into PyVista grids
    grid = manage_voxel.get_grid(n, d, c)
    voxel = manage_voxel.get_voxel(grid, idx_v)
    point = manage_voxel.get_point(voxel, data_point)

    # add the domain tag to the geometry
    voxel = manage_voxel.set_viewer_domain(voxel, idx_v, dom_v, gra_v)

    return grid, voxel, point


def _get_plot(grid, voxel, point, data_viewer, is_blocking):
    """
    Make a plot with the voxel structure and the domains.
    """

    # extract the data
    plot_type = data_viewer["plot_type"]
    data_window = data_viewer["data_window"]
    clip_options = data_viewer["clip_options"]
    plot_options = data_viewer["plot_options"]

    # get the plotter (with the Qt framework)
    pl = vistagui.open_plotter(data_window, is_blocking)

    # make the plot
    manage_plot.get_plot_viewer(pl, voxel, plot_type, clip_options)

    # add the geometry and axes
    manage_plot.get_plot_options(pl, grid, voxel, point, plot_options)

    # close plotter if non-blocking
    vistagui.close_plotter(pl, is_blocking)


def run(data_voxel, data_point, data_viewer, is_blocking):
    """
    Main script for visualizing a 3D voxel structure.
    """

    # init
    logger.info("init")

    # run the code
    try:
        # check the input data
        logger.info("check the input data")
        check_data_point.check_data_point(data_point)
        check_data_visualization.check_data_viewer(data_viewer)

        # create the Qt app (should be at the beginning)
        logger.info("create the GUI application")
        app = vistagui.open_app(is_blocking)

        # handle the data
        logger.info("parse the voxel geometry and the data")
        (grid, voxel, point) = _get_grid_voxel(data_voxel, data_point)

        # make the plots
        logger.info("generate the different plots")
        for i, dat_tmp in enumerate(data_viewer):
            logger.info("plotting %d / %d" % (i + 1, len(data_viewer)))
            _get_plot(grid, voxel, point, dat_tmp, is_blocking)
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
