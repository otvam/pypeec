"""
Generate the configuration files (viewer, and plotter files).
These configurations are dumped into JSON files.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import os.path
from pypeec import io
from examples import examples_config

# get config
PATH_ROOT = examples_config.PATH_ROOT
FOLDER_CONFIG = examples_config.FOLDER_CONFIG


def _get_plot_options(name):
    """
    The plot options are controlling the 3D wireframe rendering.
    This structure is used by the viewer and the plotter.
    """

    plot_options = {
        "title_text": name,  # name displayed on the window corner
        "title_color": "black",  # color of the text displayed on the window corner
        "title_font": 10.0,  # font size of the text displayed on the window corner
        "background_color": "gray",  # background color of the plot
        "axis_size": 2.0,  # size of the axis marker
        "grid_plot": True,  # plot (or not) the complete voxel geometry as wireframe
        "grid_thickness": 1.0,  # line thickness for the complete voxel geometry
        "grid_color": "black",  # line opacity for the complete voxel geometry
        "grid_opacity": 0.1,  # line color for the complete voxel geometry
        "geom_plot": True,  # plot (or not) the non-empty voxels as wireframe
        "geom_thickness": 1.0,  # line thickness for the non-empty voxels
        "geom_color": "black",  # line color for the non-empty voxels
        "geom_opacity": 0.5,  # line opacity for the non-empty voxels
        "point_plot": True,  # plot (or not) the provided point cloud as dots
        "point_color": "red",  # color of the point cloud dots
        "point_size": 5.0,  # size of the point cloud dots
        "point_opacity": 0.5,  # opacity of the point cloud dots
        "camera_roll": None, # camera roll angle (None for default)
        "camera_azimuth": None, # camera azimuth angle (None for default)
        "camera_elevation": None, # camera elevation angle (None for default)
    }

    return plot_options


def _get_clip_options():
    """
    Define the 3D display (with/without clipping plane).
    """

    clip_options = {
        "clip_plot": False,  # add (or not) a widget for interactive clipping
        "clip_invert": False,  # invert (or not) the clipping direction
        "clip_axis": "z",  # normal of the clipping direction
        "clip_value": 0.0,  # initial position for the clipping
    }

    return clip_options


def _get_data_window(name):
    """
    The window options are the window title and appearance.
    This structure is used by the viewer and the plotter.
    """

    data_window = {
        "title": name,  # window name
        "show_menu": False,  # show (or not) the window menu
        "image_size": (800, 600),  # initial window size, silent renderer, None for default
        "window_size": (800, 600),  # initial window size, Qt renderer, None for default
        "notebook_size": (800, 600),  # initial window size, Jupyter renderer, None for default
    }

    return data_window


def _get_data_viewer_domain(name):
    """
    Plot options for the domain description.
    The result is plotted on the voxel structure.
    This structure is used by the viewer.
    """

    data_options = {
        "colormap": "Accent",  # colormap used to plot the different voxel groups
        "opacity": 1.0,  # opacity of the face color
    }

    data = _get_data_pyvista("domain", data_options, name)

    return data


def _get_data_viewer_connection(name):
    """
    Plot options for the connection description.
    The result is plotted on the voxel structure.
    This structure is used by the viewer.
    """

    data_options = {
        "colormap": "Accent",  # colormap used to plot the different voxel groups
        "opacity": 1.0,  # opacity of the face color
    }

    data = _get_data_pyvista("connection", data_options, name)

    return data


def _get_data_viewer_voxelization(name):
    """
    Plot options for the voxelization description.
    The result is plotted on the voxel structure.
    This structure is used by the viewer.
    """

    data_options = {
        "color_voxel": "red",  # face color for the voxelized structure
        "color_reference": "blue",  # face color for the reference structure
        "opacity_voxel": 0.5,  # face opacity for the voxelized structure
        "opacity_reference": 0.5,  # face opacity for the reference structure
    }

    data = _get_data_pyvista("voxelization", data_options, name)

    return data


def _get_data_plotter_material(name):
    """
    Plot options for the material description.
    The result is plotted on the voxel structure.
    This structure is used by the plotter.
    """

    data_options = {
        "color_electric": "darkorange",  # color of the electric domains
        "color_magnetic": "gainsboro",  # color of the magnetic domains
        "color_current_source": "forestgreen",  # color of the current source domains
        "color_voltage_source": "royalblue",  # color of the voltage source domains
    }

    data = _get_data_pyvista("material", data_options, name)

    return data


def _get_data_plotter_convergence(name):
    """
    Plot options for the convergence description.
    The result is plotted on a 2D plot.
    This structure is used by the plotter.
    """

    data_options = {
        "color_active": "red",  # color of the plot for the active power
        "color_reactive": "blue",  # color of the plot for the reactive power
        "marker": "o",  # marker shape
    }

    data = _get_data_matplotlib("convergence", data_options, name)

    return data


def _get_data_plotter_residuum(name):
    """
    Plot options for the convergence description.
    The result is plotted on a 2D plot.
    This structure is used by the plotter.
    """

    data_options = {
        "n_bins": 10,  # number of bins
        "tol_bins": 0.05,  # tolerance for the bin boundaries
        "bar_color": "blue",  # fill color of the bins
        "edge_color": "black",  # edge color of the bins
    }

    data = _get_data_matplotlib("residuum", data_options, name)

    return data


def _get_data_plotter_scalar(plot_geom, var, scale, unit, name):
    """
    Plot options for a scalar variable (scalar plot).
    The variable is either plotted on the voxel structure or on a provided point cloud.
    This structure is used by the plotter.
    """

    data_options = {
        "var": var,  # name of the scalar variable to be plotted (color scale)
        "scale": scale,  # scaling of the variable (scaling done just before plotting)
        "log": False,  # use (or not) a log scale for the color axis
        "color_lim": None,  # clamping range for the color axis (None for complete range)
        "filter_lim": None,  # hide voxels/points with values outside this range (None for complete range)
        "point_size": 10.0,  # size of the marker used for plotting on the point cloud
        "legend": "%s [%s]" % (name, unit),  # legend of the color axis
    }

    data = _get_data_pyvista("scalar_" + plot_geom, data_options, name)

    return data


def _get_data_plotter_arrow(plot_geom, var_scalar, var_vector, scale, unit, name):
    """
    Plot options for a vector variable (arrow plot).
    The variable is either plotted on the voxel structure or on a provided point cloud.
    This structure is used by the plotter.
    """

    data_options = {
        "var_scalar": var_scalar,  # name of the scalar variable to be plotted (arrow color)
        "var_vector": var_vector,  # name of the vector variable to be plotted (arrow direction)
        "scale": scale,  # scaling of the scalar variable (scaling done just before plotting)
        "log": False,  # use (or not) a log scale for the color axis
        "color_lim": None,  # clamping range for the color axis (None for complete range)
        "filter_lim": None,  # hide arrows with scalar values outside this range (None for complete range)
        "arrow_threshold": 1e-3,  # relative threshold for arrows with small scalar values
        "arrow_scale": 0.75,  # relative arrow length (with respect to the voxel size)
        "legend": "%s [%s]" % (name, unit),  # legend of the color axis
    }

    data = _get_data_pyvista("arrow_" + plot_geom, data_options, name)

    return data


def _get_data_pyvista(plot_type, data_options, name):
    """
    Get the options defining a single PyVista plot.
    This structure is used by the plotter.
    """

    data = {
        "plot_framework": "pyvista",
        "data_window": _get_data_window(name),
        "data_plot": {
            "plot_type": plot_type,
            "data_options": data_options,
            "clip_options": _get_clip_options(),
            "plot_options": _get_plot_options(name),
        },
    }

    return data


def _get_data_matplotlib(plot_type, data_options, name):
    """
    Get the options defining a single Matplotlib plot.
    This structure is used by the plotter.
    """

    data = {
        "plot_framework": "matplotlib",
        "data_window": _get_data_window(name),
        "data_plot": {
            "plot_type": plot_type,
            "data_options": data_options,
        },
    }

    return data


def get_data_viewer():
    """
    Get the options for visualizing the voxel structure.
    Each element in the list represents a different plot.
    This list is used by the viewer.
    """

    # get the plots
    data_viewer = {
        "domain": _get_data_viewer_domain("Domain"),
        "connection": _get_data_viewer_connection("Connection"),
        "voxelization": _get_data_viewer_voxelization("Voxelization"),
    }

    return data_viewer


def get_data_plotter():
    """
    Get the options for plotting the solver solution.
    Each element in the list represents a different plot.
    This list is used by the plotter.
    """

    # get the plots
    data_plotter = {
        "material": _get_data_plotter_material("Material"),
        "V_c_abs": _get_data_plotter_scalar("voxel", "V_c_abs", 1e0, "V", "El. Potential"),
        "V_m_abs": _get_data_plotter_scalar("voxel", "V_m_abs", 1e0, "A", "Mag. Potential"),
        "S_c_abs": _get_data_plotter_scalar("voxel", "S_c_abs", 1e-9, "A/mm3", "El. Source"),
        "Q_m_abs": _get_data_plotter_scalar("voxel", "Q_m_abs", 1e0, "mT/mm", "Mag. Source"),
        "P_c_abs": _get_data_plotter_scalar("voxel", "P_c_abs", 1e-6, "W/cm3", "El. Losses"),
        "P_m_abs": _get_data_plotter_scalar("voxel", "P_m_abs", 1e-6, "W/cm3", "Mag. Losses"),
        "J_c_norm_abs": _get_data_plotter_scalar("voxel", "J_c_norm_abs", 1e-6, "A/mm2", "Current"),
        "J_c_norm_re": _get_data_plotter_arrow("voxel", "J_c_norm_re", "J_c_vec_re", 1e-6, "A/mm2", "Re. Current"),
        "J_c_norm_im": _get_data_plotter_arrow("voxel", "J_c_norm_im", "J_c_vec_im", 1e-6, "A/mm2", "Im. Current"),
        "B_m_norm_abs": _get_data_plotter_scalar("voxel", "B_m_norm_abs", 1e3, "mT", "Flux Density"),
        "B_m_norm_re": _get_data_plotter_arrow("voxel", "B_m_norm_re", "B_m_vec_re", 1e3, "mT", "Re. Flux Density"),
        "B_m_norm_im": _get_data_plotter_arrow("voxel", "B_m_norm_im", "B_m_vec_im", 1e3, "mT", "Im. Flux Density"),
        "H_norm_abs": _get_data_plotter_scalar("point", "H_norm_abs", 1e0, "A/m", "Mag. Field Norm"),
        "H_norm_re": _get_data_plotter_arrow("point", "H_norm_re", "H_vec_re", 1e0, "A/m", "Re. Mag. Field"),
        "H_norm_im": _get_data_plotter_arrow("point", "H_norm_im", "H_vec_im", 1e0, "A/m", "Im. Mag. Field"),
        "convergence": _get_data_plotter_convergence("Convergence"),
        "residuum": _get_data_plotter_residuum("Residuum"),
    }

    return data_plotter


if __name__ == "__main__":
    # get the filenames
    file_plotter = os.path.join(PATH_ROOT, FOLDER_CONFIG, "plotter.json")
    file_viewer = os.path.join(PATH_ROOT, FOLDER_CONFIG, "viewer.json")

    # get data
    data_viewer = get_data_viewer()
    data_plotter = get_data_plotter()

    # create file
    io.write_config(file_viewer, data_viewer)
    io.write_config(file_plotter, data_plotter)
