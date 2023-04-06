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

from pypeec.lib_visualization import manage_compute
from pypeec.lib_visualization import manage_voxel
from pypeec.lib_visualization import manage_pyvista
from pypeec.lib_check import check_data_visualization
from pypeec.lib_utils import plotgui
from pypeec.lib_utils import timelogger
from pypeec.error import CheckError, RunError

# get a logger
LOGGER = timelogger.get_logger("VIEWER")


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
    reference = data_voxel["reference"]

    # get the indices of the non-empty voxels and the domain and connection description
    (idx, domain, connection) = manage_compute.get_geometry_tag(domain_def, connection_def)

    # convert the voxel geometry into PyVista grids
    grid = manage_voxel.get_grid(n, d, c)
    voxel = manage_voxel.get_voxel(grid, idx)
    point = manage_voxel.get_point(data_point, voxel)

    # add the domain tag to the geometry
    voxel = manage_voxel.set_viewer_domain(voxel, idx, domain, connection)

    return grid, voxel, point, reference


def _get_plot(tag, data_viewer, grid, voxel, point, reference, gui_obj):
    """
    Make a plot with the voxel structure and the domains.
    """

    # extract the data
    data_window = data_viewer["data_window"]
    data_plot = data_viewer["data_plot"]

    # get the plotter (with the Qt framework)
    pl = gui_obj.open_pyvista(tag, data_window)

    # make the plot
    manage_pyvista.get_plot_viewer(pl, grid, voxel, point, reference, data_plot)


def run(data_voxel, data_point, data_viewer, tag_plot=None, is_silent=False):
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
    data_viewer: dict
        The dict describes the different plots to be created.
        Different types of plots are available.
        Plot of the different domain composing the voxel structure.
        Plot of the connected components composing the voxel structure.
    tag_plot : list
        The list describes plots to be shown.
        If None, all the plots are shown.
    is_silent : boolean
        If true, the plots are not shown (non-blocking call).
        If true, the plots are shown (blocking call).

    Returns
    -------
    status : boolean
        True if the call is successful.
        False if the problems are encountered.
    ex : exception
        The encountered exception (if any).
        None if the termination is successful.
    """

    # run the code
    try:
        # check the input data
        LOGGER.info("check the input data")
        check_data_visualization.check_data_point(data_point)
        check_data_visualization.check_data_viewer(data_viewer)
        check_data_visualization.check_is_silent(is_silent)
        check_data_visualization.check_options(data_viewer, tag_plot)

        # find the plots
        if tag_plot is not None:
            data_viewer = {key: data_viewer[key] for key in tag_plot}

        # create the Qt app (should be at the beginning)
        LOGGER.info("init the plot manager")
        gui_obj = plotgui.PlotGui(is_silent)

        # handle the data
        LOGGER.info("parse the voxel geometry and the data")
        (grid, voxel, point, reference) = _get_grid_voxel(data_voxel, data_point)

        # make the plots
        with timelogger.BlockTimer(LOGGER, "generate the different plots"):
            for i, (tag_plot, data_viewer_tmp) in enumerate(data_viewer.items()):
                LOGGER.info("plotting %d / %d / %s" % (i+1, len(data_viewer), tag_plot))
                _get_plot(tag_plot, data_viewer_tmp, grid, voxel, point, reference, gui_obj)
    except (CheckError, RunError) as ex:
        timelogger.log_exception(LOGGER, ex)
        return False, ex

    # end message
    LOGGER.info("successful termination")

    # enter the event loop (should be at the end, blocking call)
    status = gui_obj.show()

    return status, None
