"""
Main script for plotting the solution of a FFT-PEEC problem.
Plot the following features:
    - material description (conductors and sources)
    - resistivity
    - potential
    - current density
    - magnetic field

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
logger = timelogger.get_logger("plotter")


def _get_grid_voxel(data_solution, data_point):
    """
    Convert the complete voxel geometry into a PyVista uniform grid.
    Convert the non-empty voxel geometry into a PyVista unstructured grid.
    Add the solver results (material description, resistivity, and field) to the grid.
    """

    # extract the data
    n = data_solution["n"]
    d = data_solution["d"]
    c = data_solution["c"]
    voxel_point = data_solution["voxel_point"]
    idx_v = data_solution["idx_v"]
    idx_src_c = data_solution["idx_src_c"]
    idx_src_v = data_solution["idx_src_v"]
    rho_v = data_solution["rho_v"]
    V_v = data_solution["V_v"]
    J_v = data_solution["J_v"]

    # compute the magnetic field
    H_point = manage_voxel.get_magnetic_field(d, idx_v, J_v, voxel_point, data_point)

    # convert the voxel geometry into PyVista grids
    grid = manage_voxel.get_grid(n, d, c)
    voxel = manage_voxel.get_voxel(grid, idx_v)
    point = manage_voxel.get_point(voxel, data_point)

    # add the problem solution to the grid
    voxel = manage_voxel.set_plotter_material(voxel, idx_v, idx_src_c, idx_src_v)
    voxel = manage_voxel.set_plotter_resistivity(voxel, idx_v, rho_v)
    voxel = manage_voxel.set_plotter_potential(voxel, idx_v, V_v)
    voxel = manage_voxel.set_plotter_current_density(voxel, idx_v, J_v)
    point = manage_voxel.set_plotter_magnetic_field(point, H_point)

    return grid, voxel, point


def _get_plot(grid, voxel, point, data_plotter, is_blocking):
    """
    Make a plot with the specified user settings.
    The plot contains the following elements:
        - the geometry as wireframe
        - the axis, color bar, and legend
        - the payload (material description, scalar plots, or arrow plots)
    """

    # extract the data
    plot_type = data_plotter["plot_type"]
    plot_geom = data_plotter["plot_geom"]
    data_window = data_plotter["data_window"]
    data_options = data_plotter["data_options"]
    clip_options = data_plotter["clip_options"]
    plot_options = data_plotter["plot_options"]

    # get the plotter (with the Qt framework)
    pl = vistagui.open_plotter(data_window, is_blocking)

    # find the plot type and call the corresponding function
    manage_plot.get_plot_plotter(pl, grid, voxel, point, plot_type, plot_geom, data_options, clip_options)

    # add the geometry and axes
    manage_plot.get_plot_options(pl, grid, voxel, point, plot_options)

    # close plotter if non-blocking
    vistagui.close_plotter(pl, is_blocking)


def run(data_solution, data_point, data_plotter, is_blocking):
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
        check_data_point.check_data_point(data_point)
        check_data_visualization.check_data_plotter(data_plotter)

        # create the Qt app (should be at the beginning)
        logger.info("create the GUI application")
        app = vistagui.open_app(is_blocking)

        # handle the data
        logger.info("parse the voxel geometry and the data")
        (grid, voxel, point) = _get_grid_voxel(data_solution, data_point)

        # make the plots
        logger.info("generate the different plots")
        for i, dat_tmp in enumerate(data_plotter):
            logger.info("plotting %d / %d" % (i + 1, len(data_plotter)))
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
