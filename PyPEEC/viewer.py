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
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

from PyPEEC.lib_visualization import manage_compute
from PyPEEC.lib_visualization import manage_voxel
from PyPEEC.lib_visualization import manage_pyvista
from PyPEEC.lib_check import check_data_point
from PyPEEC.lib_check import check_data_visualization
from PyPEEC.lib_utils import plotgui
from PyPEEC.lib_utils import timelogger
from PyPEEC.lib_utils.error import CheckError, RunError

# get a logger
logger = timelogger.get_logger("VIEWER")


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
    connection_def = data_voxel["connection_def"]
    mesh_all = data_voxel["mesh_all"]

    # get the indices of the non-empty voxels and the domain and connection description
    (idx, domain, connection) = manage_compute.get_geometry_tag(domain_def, connection_def)

    # convert the voxel geometry into PyVista grids
    grid = manage_voxel.get_grid(n, d, c)
    voxel = manage_voxel.get_voxel(grid, idx)
    point = manage_voxel.get_point(data_point, voxel)

    # add the domain tag to the geometry
    voxel = manage_voxel.set_viewer_domain(voxel, idx, domain, connection)

    return grid, voxel, point, mesh_all


def _get_plot(grid, voxel, point, mesh_all, data_viewer, is_interactive):
    """
    Make a plot with the voxel structure and the domains.
    """

    # extract the data
    data_window = data_viewer["data_window"]
    data_plot = data_viewer["data_plot"]

    # get the plotter (with the Qt framework)
    pl = plotgui.open_pyvista(data_window, is_interactive)

    # make the plot
    manage_pyvista.get_plot_viewer(pl, grid, voxel, point, mesh_all, data_plot)

    # close plotter if non-interactive
    plotgui.close_pyvista(pl, is_interactive)


def run(data_voxel, data_point, data_viewer, is_interactive):
    """
    Main script for visualizing a 3D voxel structure.
    Handle invalid data with exceptions.

    Parameters
    ----------
    data_voxel : dict
        The dict describes the voxel structure.
        The voxel grid (number, size, and origin) is defined.
        Different domains (with the indices of the voxel) are defined.
        The connected components of the graph defined by the voxel structure are defined.
    data_point: list
        The array describes a point cloud.
        The cloud point will be used for field evaluation.
    data_viewer: list
        The list describes the different plots to be created.
        Different types of plots are available.
        Plot of the different domain composing the voxel structure.
        Plot of the connected components composing the voxel structure.
    is_interactive : boolean
        If true, the plots are shown (blocking call).
        If false, the plots are not shown (non-blocking call).

    Returns
    -------
    status : status (boolean)
        True if the call is successful.
        False if the problems are encountered
    """

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
        (grid, voxel, point, mesh_all) = _get_grid_voxel(data_voxel, data_point)

        # make the plots
        logger.info("generate the different plots")
        for i, dat_tmp in enumerate(data_viewer):
            logger.info("plotting %d / %d" % (i+1, len(data_viewer)))
            _get_plot(grid, voxel, point, mesh_all, dat_tmp, is_interactive)
    except (CheckError, RunError) as ex:
        timelogger.log_exception(logger, ex)
        return False, ex

    # end message
    logger.info("successful termination")

    # enter the event loop (should be at the end, blocking call)
    logger.info("entering the GUI event loop")
    status = plotgui.run_app(app, is_interactive)
    logger.info("exiting the GUI event loop")

    return status, None
