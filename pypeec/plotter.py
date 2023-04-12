"""
Main script for plotting the solution of a PEEC problem.
Plot the following features:
    - material description
    - potential (electric and magnetic)
    - current density divergence and magnetic charges
    - current density and flux density
    - magnetic field
    - solver convergence

Two different mode are available for the plots:
    - interactive mode: the plots are shown (blocking call at the end)
    - silent mode: nothing is shown and the program exit (for debugging and testing)

The 3D plots are done with PyVista with the Qt framework.
The 2D plots are done with Matplotlib with the Qt framework.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

from pypeec.lib_visualization import manage_compute
from pypeec.lib_visualization import manage_voxel
from pypeec.lib_visualization import manage_pyvista
from pypeec.lib_visualization import manage_matplotlib
from pypeec.lib_visualization import manage_plotgui
from pypeec.lib_check import check_data_visualization
from pypeec import utils_log
from pypeec.error import CheckError, RunError

# get a logger
LOGGER = utils_log.get_logger("PLOTTER")


def _get_grid_voxel(data_init, data_sweep, data_point):
    """
    Convert the complete voxel geometry into a PyVista uniform grid.
    Convert the non-empty voxel geometry into a PyVista unstructured grid.
    Add the solver results to the grid.
    """

    # extract the data
    n = data_init["n"]
    d = data_init["d"]
    c = data_init["c"]
    pts_net_c = data_init["pts_net_c"]
    pts_net_m = data_init["pts_net_m"]
    idx_vc = data_init["idx_vc"]
    idx_vm = data_init["idx_vm"]
    idx_src_c = data_init["idx_src_c"]
    idx_src_v = data_init["idx_src_v"]

    # extract the data
    V_vc = data_sweep["V_vc"]
    V_vm = data_sweep["V_vm"]
    J_vc = data_sweep["J_vc"]
    B_vm = data_sweep["B_vm"]
    S_vc = data_sweep["S_vc"]
    Q_vm = data_sweep["Q_vm"]
    P_vc = data_sweep["P_vc"]
    P_vm = data_sweep["P_vm"]
    res = data_sweep["res"]
    conv = data_sweep["conv"]

    # get the voxel indices and the material description
    (idx, material) = manage_compute.get_material_tag(idx_vc, idx_vm, idx_src_c, idx_src_v)

    # compute the magnetic field
    H_point = manage_compute.get_magnetic_field(d, J_vc, Q_vm, pts_net_c, pts_net_m, data_point)

    # convert the voxel geometry into PyVista grids
    grid = manage_voxel.get_grid(n, d, c)
    voxel = manage_voxel.get_voxel(grid, idx)
    point = manage_voxel.get_point(data_point, voxel)

    # add the problem solution to the grid
    voxel = manage_voxel.set_plotter_voxel_material(voxel, idx, material)

    # set the electric variables
    voxel = manage_voxel.set_plotter_voxel_scalar(voxel, idx, idx_vc, V_vc, "V_c")
    voxel = manage_voxel.set_plotter_voxel_scalar(voxel, idx, idx_vc, S_vc, "S_c")
    voxel = manage_voxel.set_plotter_voxel_scalar(voxel, idx, idx_vc, P_vc, "P_c")
    voxel = manage_voxel.set_plotter_voxel_vector(voxel, idx, idx_vc, J_vc, "J_c")

    # set the magnetic variables
    voxel = manage_voxel.set_plotter_voxel_scalar(voxel, idx, idx_vm, V_vm, "V_m")
    voxel = manage_voxel.set_plotter_voxel_scalar(voxel, idx, idx_vm, Q_vm, "Q_m")
    voxel = manage_voxel.set_plotter_voxel_scalar(voxel, idx, idx_vm, P_vm, "P_m")
    voxel = manage_voxel.set_plotter_voxel_vector(voxel, idx, idx_vm, B_vm, "B_m")

    # add the magnetic field
    point = manage_voxel.set_plotter_magnetic_field(point, H_point)

    return grid, voxel, point, res, conv


def _get_plot(tag, data_plotter, grid, voxel, point, res, conv, gui_obj):
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
        pl = gui_obj.open_pyvista(tag, data_window)

        # make the plot
        manage_pyvista.get_plot_plotter(pl, grid, voxel, point, data_plot)
    elif plot_framework == "matplotlib":
        # get the figure (with the Qt framework)
        fig = gui_obj.open_matplotlib(tag, data_window)

        # make the plot
        manage_matplotlib.get_plot_plotter(fig, res, conv, data_plot)
    else:
        raise ValueError("invalid plot framework")


def _get_sweep(tag_sweep, data_sweep, data_init, data_point, data_plotter, gui_obj):
    """
    Parse the geometry and make the plots for a specified sweep.
    """

    # handle the data
    LOGGER.info("parse the voxel geometry and the data")
    (grid, voxel, point, res, conv) = _get_grid_voxel(data_init, data_sweep, data_point)

    # make the plots
    with utils_log.BlockTimer(LOGGER, "generate the different plots"):
        for i, (tag_plot, data_plotter_tmp) in enumerate(data_plotter.items()):
            LOGGER.info("plotting %d / %d / %s" % (i + 1, len(data_plotter), tag_plot))
            _get_plot(tag_sweep + " / " + tag_plot, data_plotter_tmp, grid, voxel, point, res, conv, gui_obj)


def run(data_solution, data_point, data_plotter, tag_sweep=None, tag_plot=None, is_silent=False):
    """
    Main script for plotting the solution of a PEEC problem.
    Handle invalid data with exceptions.

    Parameters
    ----------
    data_solution:  dict
        The dict describes the problem solution.
        The voxel structure is defined.
        The frequency of the problem is defined.
        The status of the solution (solver convergence and condition number) is described.
        The potential, current density, and flux density of the different voxel are defined.
        The terminals quantities (voltage and current) of the sources are defined.
        The integral quantities (total losses and energy) of the problem are defined.
    data_point: list
        The array describes a point cloud.
        The cloud point is used for field evaluation.
    data_plotter: dict
        The dict describes the different plots to be created.
        Different types of plots are available.
        Plot showing the materials and sources.
        Scalar plot of the potential (electric and magnetic) on the voxels.
        Scalar plot of the current density divergence and magnetic charges on the voxels.
        Scalar plot of the current density and flux density on the voxels.
        Vector plot (with arrows) of the current density and flux density on the voxels.
        Scalar plot of the magnetic field on the point cloud.
        Vector plot (with arrows) of the magnetic field on the point cloud.
        Plots describing the solver convergence.
    tag_sweep : list
        The list describes sweeps to be shown.
        If None, all the sweeps are shown.
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
        # extract the data
        data_init = data_solution["data_init"]
        data_sweep = data_solution["data_sweep"]

        # check the input data
        LOGGER.info("check the input data")
        check_data_visualization.check_data_point(data_point)
        check_data_visualization.check_data_plotter(data_plotter)
        check_data_visualization.check_is_silent(is_silent)
        check_data_visualization.check_options(data_sweep, tag_sweep)
        check_data_visualization.check_options(data_plotter, tag_plot)

        # find the plots
        if tag_sweep is not None:
            data_sweep = {key: data_sweep[key] for key in tag_sweep}
        if tag_plot is not None:
            data_plotter = {key: data_plotter[key] for key in tag_plot}

        # create the Qt app (should be at the beginning)
        LOGGER.info("init the plot manager")
        gui_obj = manage_plotgui.PlotGui(is_silent)

        # plot the sweeps
        for tag_sweep, data_sweep_tmp in data_sweep.items():
            with utils_log.BlockTimer(LOGGER, "plot sweep: " + tag_sweep):
                _get_sweep(tag_sweep, data_sweep_tmp, data_init, data_point, data_plotter, gui_obj)
    except (CheckError, RunError) as ex:
        utils_log.log_exception(LOGGER, ex)
        return False, ex

    # end message
    LOGGER.info("successful termination")

    # enter the event loop (should be at the end, blocking call)
    status = gui_obj.show()

    return status, None
