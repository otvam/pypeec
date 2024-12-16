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

import scilogger
from pypeec.lib_plot import parse_plotter
from pypeec.lib_plot import parse_voxel
from pypeec.lib_plot import manage_pyvista
from pypeec.lib_plot import manage_matplotlib
from pypeec.lib_plot import manage_plotgui
from pypeec.lib_check import check_data_format
from pypeec.lib_check import check_data_options

# get a logger
LOGGER = scilogger.get_logger(__name__, "pypeec")


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
    var = data_sweep["var"]
    res = data_sweep["res"]
    conv = data_sweep["conv"]

    # get voxel indices
    idx = parse_plotter.get_voxel(idx_vc, idx_vm)

    # convert the voxel geometry into PyVista grids
    grid = parse_voxel.get_grid(n, d, c)
    voxel = parse_voxel.get_voxel(grid, idx)
    point = parse_voxel.get_point(pts_cloud)

    # add the problem solution to the grid
    voxel = parse_plotter.set_voxel_material(voxel, idx, idx_vc, idx_vm, idx_src_c, idx_src_v)

    # set the scalar variables
    for name, value in var.items():
        # extract variable
        var = value["var"]
        cat = value["cat"]

        # parse the variable and assign to the geometry
        if cat == "scalar_electric":
            voxel = parse_plotter.set_voxel_scalar(voxel, idx, idx_vc, var, name)
        elif cat == "scalar_magnetic":
            voxel = parse_plotter.set_voxel_scalar(voxel, idx, idx_vm, var, name)
        elif cat == "vector_electric":
            voxel = parse_plotter.set_voxel_vector(voxel, idx, idx_vc, var, name)
        elif cat == "vector_magnetic":
            voxel = parse_plotter.set_voxel_vector(voxel, idx, idx_vm, var, name)
        elif cat == "cloud":
            point = parse_plotter.set_point_cloud(point, var, name)
        else:
            raise ValueError("invalid variable type")

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
    layout = data_plotter["layout"]
    data_window = data_plotter["data_window"]
    data_plot = data_plotter["data_plot"]
    data_options = data_plotter["data_options"]

    # make the plots
    if framework == "pyvista":
        # get the plotter (with the Qt framework)
        pl = gui_obj.open_pyvista(tag, data_window)

        # make the plot
        manage_pyvista.get_plot_plotter(pl, grid, voxel, point, layout, data_plot, data_options)
    elif framework == "matplotlib":
        # get the figure (with the Qt framework)
        fig = gui_obj.open_matplotlib(tag, data_window)

        # make the plot
        manage_matplotlib.get_plot_plotter(fig, res, conv, layout, data_plot, data_options)
    else:
        raise ValueError("invalid plot framework")


def _get_sweep(tag_sweep, data_sweep, data_init, data_plotter, gui_obj):
    """
    Parse the geometry and make the plots for a specified sweep.
    """

    # handle the data
    (grid, voxel, point, res, conv) = _get_grid_voxel(data_init, data_sweep)

    # add the raw VTK objects
    gui_obj.open_vtk(tag_sweep + "_grid", grid)
    gui_obj.open_vtk(tag_sweep + "_voxel", voxel)
    gui_obj.open_vtk(tag_sweep + "_point", point)

    # make the plots
    for tag_plot, data_plotter_tmp in data_plotter.items():
        LOGGER.info("plot / %s" % tag_plot)
        _get_plot(tag_sweep + "_" + tag_plot, data_plotter_tmp, grid, voxel, point, res, conv, gui_obj)


def run(
    data_solution,
    data_plotter,
    tag_sweep=None,
    tag_plot=None,
    plot_mode=None,
    folder=None,
    name=None,
):
    """
    Main script for plotting the solution of a PEEC problem.
    Handle invalid data with exceptions.
    """

    # check the solution data
    LOGGER.info("check the solution data")
    (status, data_init, data_sweep) = check_data_options.check_data_solution(data_solution)
    if not status:
        LOGGER.warning("invalid status for the solution data")

    # check the input data
    LOGGER.info("check the input data")
    check_data_format.check_data_plotter(data_plotter)
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
        LOGGER.info("plot sweep: " + tag_sweep)
        with LOGGER.BlockIndent():
            _get_sweep(tag_sweep, data_sweep_tmp, data_init, data_plotter, gui_obj)

    # enter the event loop (should be at the end, blocking call)
    gui_obj.show()
