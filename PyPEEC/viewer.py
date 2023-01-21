"""
Main script for visualizing a 3D voxel structure.
Plot the following features:
    - the different domain composing the voxel structure
    - the connected components of the voxel structure

Two different mode are available for the plots:
    - interactive mode: the plots are shown (blocking call at the end)
    - silent mode: nothing is shown and the program exit (for debugging and testing)

The plotting is done with PyVista with the Qt framework.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

from PyPEEC.lib_visualization import manage_voxel
from PyPEEC.lib_visualization import manage_pyvista
from PyPEEC.lib_check import check_data_point
from PyPEEC.lib_check import check_data_visualization
from PyPEEC.lib_utils import plotgui
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


def _get_plot(grid, voxel, point, data_viewer, is_interactive):
    """
    Make a plot with the voxel structure and the domains.
    """

    # extract the data
    data_window = data_viewer["data_window"]
    data_plot = data_viewer["data_plot"]

    # get the plotter (with the Qt framework)
    pl = plotgui.open_pyvista(data_window, is_interactive)

    # make the plot
    manage_pyvista.get_plot_viewer(pl, grid, voxel, point, data_plot)

    # close plotter if non-interactive
    plotgui.close_pyvista(pl, is_interactive)


def run(data_voxel, data_point, data_viewer, is_interactive):
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
        app = plotgui.open_app(is_interactive)

        # handle the data
        logger.info("parse the voxel geometry and the data")
        (grid, voxel, point) = _get_grid_voxel(data_voxel, data_point)

        # make the plots
        logger.info("generate the different plots")
        for i, dat_tmp in enumerate(data_viewer):
            logger.info("plotting %d / %d" % (i + 1, len(data_viewer)))
            _get_plot(grid, voxel, point, dat_tmp, is_interactive)
    except CheckError as ex:
        logger.error("check error : " + str(ex))
        return False
    except RunError as ex:
        logger.error("check error : " + str(ex))
        return False

    # end message
    logger.info("successful termination")

    # enter the event loop (should be at the end, blocking call)
    status = plotgui.run_app(app, is_interactive)

    return status
