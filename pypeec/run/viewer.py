"""
Main script for visualizing a 3D voxel structure.

Plot the following features:
    - The different domains composing the voxel structure.
    - The connected components of the voxel structure.
    - The deviation between the original geometry and the voxel structure.
    - A matrix showing which domains are adjacent/connected to each others.

Several plot modes are available:
    - The Qt framework is used for rendering the plots.
    - Interactive plots are rendered within the Jupyter notebook.
    - Static plots are rendered within the Jupyter notebook.
    - The plot content are saved as PNG files.
    - The plot data are saved as VTK files.
    - The plots are not shown (debug mode).
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import scilogger
from pypeec.lib_plot import parse_viewer
from pypeec.lib_plot import parse_voxel
from pypeec.lib_plot import manage_pyvista
from pypeec.lib_plot import manage_matplotlib
from pypeec.lib_plot import manage_plotgui
from pypeec.lib_check import check_data_format
from pypeec.lib_check import check_data_options

# get a logger
LOGGER = scilogger.get_logger(__name__, "pypeec")


def _get_grid_voxel(data_voxel):
    """
    Convert the complete voxel geometry into a PyVista uniform grid.
    Convert the non-empty voxel geometry into a PyVista unstructured grid.
    Convert the point cloud into a PyVista polydata object.
    Add the domains and connected components to the geometry.
    """

    # extract the data
    n = data_voxel["n"]
    d = data_voxel["d"]
    c = data_voxel["c"]
    domain_def = data_voxel["domain_def"]
    component_def = data_voxel["component_def"]
    connect_def = data_voxel["connect_def"]
    pts_cloud = data_voxel["pts_cloud"]
    geom_def = data_voxel["geom_def"]

    # get voxel indices
    idx = parse_viewer.get_voxel(domain_def)

    # convert the voxel geometry into PyVista grids
    grid = parse_voxel.get_grid(n, d, c)
    voxel = parse_voxel.get_voxel(grid, idx)
    point = parse_voxel.get_point(pts_cloud)
    reference = parse_voxel.get_reference(geom_def)

    # add the domains and connected components to the geometry
    voxel = parse_viewer.set_data(voxel, idx, domain_def, component_def)

    return grid, voxel, point, reference, connect_def


def _get_plot(tag, data_viewer, grid, voxel, point, reference, connect_def, gui_obj):
    """
    Make a plot with the specified user settings.
    """

    # extract the data
    framework = data_viewer["framework"]
    layout = data_viewer["layout"]
    data_window = data_viewer["data_window"]
    data_plot = data_viewer["data_plot"]
    data_options = data_viewer["data_options"]

    # make the plots
    if framework == "pyvista":
        # get the plotter
        pl = gui_obj.open_pyvista(tag, data_window)

        # make the plot
        manage_pyvista.get_plot_viewer(pl, grid, voxel, point, reference, layout, data_plot, data_options)
    elif framework == "matplotlib":
        # get the figure
        fig = gui_obj.open_matplotlib(tag, data_window)

        # make the plot
        manage_matplotlib.get_plot_viewer(fig, connect_def, layout, data_plot, data_options)
    else:
        raise ValueError("invalid plot framework")


def run(
    data_voxel,
    data_viewer,
    tag_plot=None,
    plot_mode=None,
    path=None,
    name=None,
):
    """
    Main script for visualizing a 3D voxel structure.
    Handle invalid data with exceptions.
    """

    # check the input data
    LOGGER.info("check the input data")
    check_data_format.check_data_viewer(data_viewer)
    check_data_options.check_plot_options(plot_mode, path, name)
    check_data_options.check_tag_list(data_viewer, tag_plot)

    # find the plots
    if tag_plot is not None:
        data_viewer = {key: data_viewer[key] for key in tag_plot}

    # create the Qt app (should be at the beginning)
    LOGGER.info("init the plot manager")
    gui_obj = manage_plotgui.PlotGui(plot_mode, path, name)

    # handle the data
    LOGGER.info("parse data")
    (grid, voxel, point, reference, connect_def) = _get_grid_voxel(data_voxel)

    # make the plots
    LOGGER.info("generate plots")
    with LOGGER.BlockIndent():
        for tag_plot, data_viewer_tmp in data_viewer.items():
            LOGGER.info("plot / %s", tag_plot)
            _get_plot(tag_plot, data_viewer_tmp, grid, voxel, point, reference, connect_def, gui_obj)

    # add the raw VTK objects
    gui_obj.open_vtk("grid", grid)
    gui_obj.open_vtk("voxel", voxel)
    gui_obj.open_vtk("point", point)
    gui_obj.open_vtk("reference", reference)

    # enter the event loop (should be at the end, blocking call)
    gui_obj.show()
