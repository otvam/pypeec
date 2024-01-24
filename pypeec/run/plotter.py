"""
Main script for plotting the solution of a PEEC problem.
Plot the following features:
    - material description
    - potential (electric and magnetic)
    - current density divergence and magnetic charges
    - current density and flux density
    - magnetic field
    - solver convergence

Three different mode are available for the plots:
    - windowed mode: with the Qt Framework
    - notebook mode: with Jupyter notebook
    - silent mode: nothing is shown and the program exit

The 3D plots are generated with PyVista.
The 2D plots are generated with Matplotlib.
The plots can be saved as PNG images.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

from pypeec.lib_visualization import data_plotter
from pypeec.lib_visualization import data_voxel
from pypeec.lib_visualization import manage_pyvista
from pypeec.lib_visualization import manage_matplotlib
from pypeec.lib_visualization import manage_plotgui
from pypeec.lib_check import check_data_visualization
from pypeec.lib_check import check_data_options
from pypeec import log

# get a logger
LOGGER = log.get_logger("PLOTTER")


def _get_grid_voxel(data_init, data_sweep):
    """
    Convert the complete voxel geometry into a PyVista uniform grid.
    Convert the non-empty voxel geometry into a PyVista unstructured grid.
    Add the solver results to the grid.
    """

    # extract the data
    n = data_init["n"]
    d = data_init["d"]
    c = data_init["c"]
    idx_vc = data_init["idx_vc"]
    idx_vm = data_init["idx_vm"]
    idx_src_c = data_init["idx_src_c"]
    idx_src_v = data_init["idx_src_v"]
    pts_cloud = data_init["pts_cloud"]

    # extract the data
    V_vc = data_sweep["V_vc"]
    V_vm = data_sweep["V_vm"]
    J_vc = data_sweep["J_vc"]
    B_vm = data_sweep["B_vm"]
    S_vc = data_sweep["S_vc"]
    Q_vm = data_sweep["Q_vm"]
    P_vc = data_sweep["P_vc"]
    P_vm = data_sweep["P_vm"]
    H_pts = data_sweep["H_pts"]
    res = data_sweep["res"]
    conv = data_sweep["conv"]

    # get voxel indices
    idx = data_plotter.get_voxel(idx_vc, idx_vm)

    # convert the voxel geometry into PyVista grids
    grid = data_voxel.get_grid(n, d, c)
    voxel = data_voxel.get_voxel(grid, idx)
    point = data_voxel.get_point(pts_cloud)

    # add the problem solution to the grid
    voxel = data_plotter.set_voxel_material(voxel, idx, idx_vc, idx_vm, idx_src_c, idx_src_v)

    # set the electric variables
    voxel = data_plotter.set_voxel_scalar(voxel, idx, idx_vc, V_vc, "V_c")
    voxel = data_plotter.set_voxel_scalar(voxel, idx, idx_vc, S_vc, "S_c")
    voxel = data_plotter.set_voxel_scalar(voxel, idx, idx_vc, P_vc, "P_c")
    voxel = data_plotter.set_voxel_vector(voxel, idx, idx_vc, J_vc, "J_c")

    # set the magnetic variables
    voxel = data_plotter.set_voxel_scalar(voxel, idx, idx_vm, V_vm, "V_m")
    voxel = data_plotter.set_voxel_scalar(voxel, idx, idx_vm, Q_vm, "Q_m")
    voxel = data_plotter.set_voxel_scalar(voxel, idx, idx_vm, P_vm, "P_m")
    voxel = data_plotter.set_voxel_vector(voxel, idx, idx_vm, B_vm, "B_m")

    # add the magnetic field
    point = data_plotter.set_magnetic_field(point, H_pts)

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
    framework = data_plotter["framework"]
    title = data_plotter["title"]
    layout = data_plotter["layout"]
    data_window = data_plotter["data_window"]
    data_plot = data_plotter["data_plot"]
    data_options = data_plotter["data_options"]

    # make the plots
    if framework == "pyvista":
        # get the plotter (with the Qt framework)
        pl = gui_obj.open_pyvista(tag, title, data_window)

        # make the plot
        manage_pyvista.get_plot_plotter(pl, grid, voxel, point, layout, data_plot, data_options)
    elif framework == "matplotlib":
        # get the figure (with the Qt framework)
        fig = gui_obj.open_matplotlib(tag, title, data_window)

        # make the plot
        manage_matplotlib.get_plot_plotter(fig, res, conv, layout, data_plot, data_options)
    else:
        raise ValueError("invalid plot framework")


def _get_sweep(tag_sweep, data_sweep, data_init, data_plotter, gui_obj):
    """
    Parse the geometry and make the plots for a specified sweep.
    """

    # handle the data
    LOGGER.info("parse data")
    (grid, voxel, point, res, conv) = _get_grid_voxel(data_init, data_sweep)

    # make the plots
    with log.BlockTimer(LOGGER, "generate plots"):
        for i, (tag_plot, data_plotter_tmp) in enumerate(data_plotter.items()):
            LOGGER.info("plotting %d / %d / %s" % (i + 1, len(data_plotter), tag_plot))
            _get_plot(tag_sweep + "_" + tag_plot, data_plotter_tmp, grid, voxel, point, res, conv, gui_obj)


def run(
        data_solution, data_plotter,
        tag_sweep=None, tag_plot=None, plot_mode="qt", folder=".", name=None
):
    """
    Main script for plotting the solution of a PEEC problem.
    Handle invalid data with exceptions.
    """

    # check the solution data
    LOGGER.info("check the solution data")
    (data_init, data_sweep) = check_data_options.check_data_solution(data_solution)

    # check the input data
    LOGGER.info("check the input data")
    check_data_visualization.check_data_plotter(data_plotter)
    check_data_options.check_plot_options(plot_mode, folder, name)
    check_data_options.check_tag_list(data_sweep, tag_sweep)
    check_data_options.check_tag_list(data_plotter, tag_plot)

    # find the plots
    if tag_sweep is not None:
        data_sweep = {key: data_sweep[key] for key in tag_sweep}
    if tag_plot is not None:
        data_plotter = {key: data_plotter[key] for key in tag_plot}

    # create the Qt app (should be at the beginning)
    LOGGER.info("init the plot manager")
    gui_obj = manage_plotgui.PlotGui(plot_mode, folder, name)

    # plot the sweeps
    for tag_sweep, data_sweep_tmp in data_sweep.items():
        with log.BlockTimer(LOGGER, "plot sweep: " + tag_sweep):
            _get_sweep(tag_sweep, data_sweep_tmp, data_init, data_plotter, gui_obj)

    # enter the event loop (should be at the end, blocking call)
    gui_obj.show()
