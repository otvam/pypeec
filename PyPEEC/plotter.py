"""
Main script for plotting the solution of a FFT-PEEC problem.
Plot the following features:
    - material description (conductors and sources)
    - resistivity
    - potential
    - current density
    - loss density
    - magnetic flux density
    - magnetic field

Two different mode are available for the plots:
    - interactive mode: the plots are shown (blocking call at the end)
    - silent mode: nothing is shown and the program exit (for debugging and testing)

The plotting is done with PyVista with the Qt framework.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

from PyPEEC.lib_visualization import manage_voxel
from PyPEEC.lib_visualization import manage_pyvista
from PyPEEC.lib_visualization import manage_matplotlib
from PyPEEC.lib_check import check_data_point
from PyPEEC.lib_check import check_data_visualization
from PyPEEC.lib_utils import plotgui
from PyPEEC.lib_utils import timelogger
from PyPEEC.lib_utils.error import CheckError, RunError

# get a logger
logger = timelogger.get_logger("PLOTTER")


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
    P_v = data_solution["P_v"]
    W_v = data_solution["W_v"]
    solver_status = data_solution["solver_status"]

    # compute the magnetic field
    H_point = manage_voxel.get_magnetic_field(d, idx_v, J_v, voxel_point, data_point)

    # convert the voxel geometry into PyVista grids
    grid = manage_voxel.get_grid(n, d, c)
    voxel = manage_voxel.get_voxel(grid, idx_v)
    point = manage_voxel.get_point(voxel, data_point)

    # add the problem solution to the grid
    voxel = manage_voxel.set_plotter_voxel_material(voxel, idx_v, idx_src_c, idx_src_v)
    voxel = manage_voxel.set_plotter_voxel_data(voxel, idx_v, rho_v, V_v, J_v, P_v, W_v)
    point = manage_voxel.set_plotter_magnetic_field(point, H_point)

    return grid, voxel, point, solver_status


def _get_plot(grid, voxel, point, solver_status, data_plotter, is_interactive):
    """
    Make a plot with the specified user settings.
    The plot contains the following elements:
        - the geometry as wireframe
        - the axis, color bar, and legend
        - the payload (material description, scalar plots, or arrow plots)
    """

    # extract the data
    plot_framework = data_plotter["plot_framework"]
    data_window = data_plotter["data_window"]
    data_plot = data_plotter["data_plot"]

    # make the plots
    if plot_framework == "pyvista":
        # get the plotter (with the Qt framework)
        pl = plotgui.open_pyvista(data_window, is_interactive)

        # make the plot
        manage_pyvista.get_plot_plotter(pl, grid, voxel, point, data_plot)

        # close plotter if non-interactive
        plotgui.close_pyvista(pl, is_interactive)
    elif plot_framework == "matplotlib":
        # get the figure (with the Qt framework)
        fig = plotgui.open_matplotlib(data_window, is_interactive)

        # make the plot
        manage_matplotlib.get_plot_plotter(fig, solver_status, data_plot)

        # close figure if non-interactive
        plotgui.close_matplotlib(fig, is_interactive)
    else:
        raise ValueError("invalid plot framework")


def run(data_solution, data_point, data_plotter, is_interactive):
    """
    Main script for plotting the solution of a FFT-PEEC problem.
    Handle invalid data with exceptions.

    Parameters
    ----------
    data_solution :  dict
        The dict describes the problem solution.
        The voxel structure is defined.
        The frequency of the problem is defined.
        The status of the solution (solver convergence and condition number) is described.
        The resistivity, potential, and current density of the different voxel are defined.
        The loss density, and magnetic flux density of the different voxel are defined.
        The terminals quantities (voltage and current) of the sources are defined.
        The integral quantities (total losses and energy) of the problem are defined.
    data_point: list
        The array describes a point cloud.
        The cloud point is used for field evaluation.
    data_plotter: list
        The list describes the different plots to be created.
        Different types of plots are available.
        Plot showing the conductors and sources.
        Scalar plot of the resistivity of the voxels.
        Scalar plot of the potential and current density of the voxels.
        Scalar plot of the loss density and magnetic flux density of the voxels.
        Vector plot (with arrows) of the current density of the voxels.
        Scalar plot of the magnetic field of the point cloud.
        Vector plot (with arrows) of the magnetic field of the point cloud.
        Plots describing the solver convergence.
    is_interactive : boolean
        If true, the plots are shown (blocking call).
        If false, the plots are not shown (non-blocking call).

    Returns
    -------
    status : boolean
        True if the call is successful.
        False if the problems are encountered
    """

    # run the code
    try:
        # check the input data
        logger.info("check the input data")
        # check the data type
        check_data_point.check_data_point(data_point)
        check_data_visualization.check_data_plotter(data_plotter)

        # create the Qt app (should be at the beginning)
        logger.info("create the GUI application")
        app = plotgui.open_app(is_interactive)

        # handle the data
        logger.info("parse the voxel geometry and the data")
        (grid, voxel, point, solver_status) = _get_grid_voxel(data_solution, data_point)

        # make the plots
        logger.info("generate the different plots")
        for i, dat_tmp in enumerate(data_plotter):
            logger.info("plotting %d / %d" % (i+1, len(data_plotter)))
            _get_plot(grid, voxel, point, solver_status, dat_tmp, is_interactive)
    except (CheckError, RunError) as ex:
        timelogger.log_exception(logger, ex)
        return False, ex

    # end message
    logger.info("successful termination")

    # enter the event loop (should be at the end, blocking call)
    logger.info("entering the event loop")
    status = plotgui.run_app(app, is_interactive)
    logger.info("exiting the event loop")

    return status, None
