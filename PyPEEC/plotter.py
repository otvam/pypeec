"""
Main script for plotting the solution of a FFT-PEEC problem.
Plot the material description, the resistivity, the potential, and the current density.

The plotting is done with PyVista with the Qt framework.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

from PyPEEC.lib_plotter import manage_voxel
from PyPEEC.lib_plotter import manage_plot
from PyPEEC.lib_shared import check_data_plotter
from PyPEEC.lib_utils import vistagui
from PyPEEC.lib_utils import timelogger
from PyPEEC.lib_utils.error import CheckError, RunError

# get a logger
logger = timelogger.get_logger("plotter")


def _get_grid_voxel(data_solution):
    """
    Convert the complete voxel geometry into a PyVista uniform grid.
    Convert the non-empty voxel geometry into a PyVista unstructured grid.
    Add the solver results (material description, resistivity, and field) to the grid.
    """

    # extract the data
    n = data_solution["n"]
    d = data_solution["d"]
    idx_v = data_solution["idx_v"]
    idx_src_c = data_solution["idx_src_c"]
    idx_src_v = data_solution["idx_src_v"]
    rho_v = data_solution["rho_v"]
    V_v = data_solution["V_v"]
    J_v = data_solution["J_v"]

    # convert the voxel geometry into PyVista grids
    (grid, geom) = manage_voxel.get_grid_geom(n, d, idx_v)

    # add the problem solution to the grid
    geom = manage_voxel.get_material(geom, idx_v, idx_src_c, idx_src_v)
    geom = manage_voxel.get_resistivity(geom, idx_v, rho_v)
    geom = manage_voxel.get_potential(geom, idx_v, V_v)
    geom = manage_voxel.get_current_density(geom, idx_v, J_v)

    return grid, geom


def _get_plot(grid, geom, data_plotter, is_blocking):
    """
    Make a plot with the specified user settings.
    The plot contains the following elements:
        - the geometry as wireframe
        - the axis, color bar, and legend
        - the payload (material description, scalar plots, or arrow plots)
    """

    # extract the data
    plot_type = data_plotter["plot_type"]
    data_window = data_plotter["data_window"]
    data_options = data_plotter["data_options"]
    plot_options = data_plotter["plot_options"]

    # get the plotter (with the Qt framework)
    pl = vistagui.open_plotter(data_window, is_blocking)

    # find the plot type and call the corresponding function
    if plot_type == "material":
        manage_plot.plot_material(pl, grid, geom, plot_options, data_options)
    elif plot_type == "scalar":
        manage_plot.plot_scalar(pl, grid, geom, plot_options, data_options)
    elif plot_type == "arrow":
        manage_plot.plot_arrow(pl, grid, geom, plot_options, data_options)
    else:
        raise CheckError("invalid plot type")

    # close plotter is non blocking
    vistagui.close_plotter(pl, is_blocking)


def run(data_voxel, data_plotter, is_blocking):
    """
    Main script for plotting the solution of a FFT-PEEC problem.
    """

    # init
    logger.info("init")

    # run the code
    try:
        # check the input data
        logger.info("check the input data")
        # check the data type
        check_data_plotter.check_data_plotter(data_plotter)

        # create the Qt app (should be at the beginning)
        logger.info("create the GUI application")
        app = vistagui.open_app(is_blocking)

        # handle the data
        logger.info("parse the voxel geometry and the data")
        (grid, geom) = _get_grid_voxel(data_voxel)

        # make the plots
        logger.info("generate the different plots")
        for i, dat_tmp in enumerate(data_plotter):
            logger.info("plotting %d / %d" % (i + 1, len(data_plotter)))
            _get_plot(grid, geom, dat_tmp, is_blocking)
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
