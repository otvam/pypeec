"""
Main script for plotting the solution of a PEEC problem.

Plot the following features:
    - The different materials composing the voxel structure.
    - The scalar variable for the non-empty voxels or the point cloud.
    - The phasor variable for the non-empty voxels or the point cloud.
    - The vector variable for the non-empty voxels or the point cloud.
    - The solver convergence and residuum.

Several plot modes are available:
    - The Qt framework is used for rendering the plots.
    - Interactive plots are rendered within the Jupyter notebook.
    - Static plots are rendered within the Jupyter notebook.
    - The plot images are saved as PNG files.
    - The plot data are saved as VTK files.
    - The plots are not shown (debug mode).
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
    Convert the point cloud into a PyVista polydata object.
    Add the material and source description to the geometry.
    Add the solution variables to the geometry.
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
    field_values = data_sweep["field_values"]
    solver_convergence = data_sweep["solver_convergence"]

    # get voxel indices
    idx = parse_plotter.get_voxel(idx_vc, idx_vm)

    # convert the voxel geometry into PyVista grids
    grid = parse_voxel.get_grid(n, d, c)
    voxel = parse_voxel.get_voxel(grid, idx)
    point = parse_voxel.get_point(pts_cloud)

    # add the material and source description to the geometry
    voxel = parse_plotter.set_voxel_material(voxel, idx, idx_vc, idx_vm, idx_src_c, idx_src_v)

    # add the solution variables to the geometry
    for name, value in field_values.items():
        # extract the variable
        var = value["var"]
        cat = value["cat"]

        # parse the variable and assign the results to the geometry
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

    return grid, voxel, point, solver_convergence


def _get_plot(tag_sweep, tag_plot, data_plotter, grid, voxel, point, solver_convergence, gui_obj):
    """
    Make a plot with the specified user settings.
    """

    # extract the data
    framework = data_plotter["framework"]
    layout = data_plotter["layout"]
    data_window = data_plotter["data_window"]
    data_plot = data_plotter["data_plot"]
    data_options = data_plotter["data_options"]

    # combine the plot tags
    tag = tag_sweep + "_" + tag_plot

    # make the plots
    if framework == "pyvista":
        # get the plotter
        pl = gui_obj.open_pyvista(tag, data_window)

        # make the plot
        manage_pyvista.get_plot_plotter(pl, grid, voxel, point, layout, data_plot, data_options)
    elif framework == "matplotlib":
        # get the figure
        fig = gui_obj.open_matplotlib(tag, data_window)

        # make the plot
        manage_matplotlib.get_plot_plotter(fig, solver_convergence, layout, data_plot, data_options)
    else:
        raise ValueError("invalid plot framework")


def _get_sweep(tag_sweep, data_sweep, data_init, data_plotter, gui_obj):
    """
    Parse the geometry and make the plots for a specified sweep.
    """

    # handle the data
    (grid, voxel, point, solver_convergence) = _get_grid_voxel(data_init, data_sweep)

    # add the raw VTK objects
    gui_obj.open_vtk(tag_sweep + "_grid", grid)
    gui_obj.open_vtk(tag_sweep + "_voxel", voxel)
    gui_obj.open_vtk(tag_sweep + "_point", point)

    # make the plots
    for tag_plot, data_plotter_tmp in data_plotter.items():
        LOGGER.info("plot / %s", tag_plot)
        _get_plot(tag_sweep, tag_plot, data_plotter_tmp, grid, voxel, point, solver_convergence, gui_obj)


def _run_extract_solution(data_solution):
    """
    Extract the solution data and check the status.
    """

    # extract the data
    status = data_solution["status"]
    data_init = data_solution["data_init"]
    data_sweep = data_solution["data_sweep"]

    # show warning
    if not status:
        LOGGER.warning("problem detected with the solution")

    return data_init, data_sweep


def run(
    data_solution,
    data_plotter,
    tag_sweep=None,
    tag_plot=None,
    plot_mode=None,
    path=None,
    name=None,
):
    """
    Main script for plotting the solution of a PEEC problem.
    Handle invalid data with exceptions.
    """

    # check the solution data
    LOGGER.info("check the solution data")
    (data_init, data_sweep) = _run_extract_solution(data_solution)

    # check the input data
    LOGGER.info("check the input data")
    check_data_format.check_data_plotter(data_plotter)
    check_data_options.check_plot_options(plot_mode, path, name)
    check_data_options.check_tag_list(data_sweep, tag_sweep)
    check_data_options.check_tag_list(data_plotter, tag_plot)

    # find the plots
    if tag_sweep is not None:
        data_sweep = {key: data_sweep[key] for key in tag_sweep}
    if tag_plot is not None:
        data_plotter = {key: data_plotter[key] for key in tag_plot}

    # create the Qt app (should be at the beginning)
    LOGGER.info("init the plot manager")
    gui_obj = manage_plotgui.PlotGui(plot_mode, path, name)

    # plot the sweeps
    for tag_sweep, data_sweep_tmp in data_sweep.items():
        LOGGER.info("sweep / %s", tag_sweep)
        with LOGGER.BlockIndent():
            _get_sweep(tag_sweep, data_sweep_tmp, data_init, data_plotter, gui_obj)

    # enter the event loop (should be at the end, blocking call)
    gui_obj.show()
