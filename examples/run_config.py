"""
Generate the configuration files (tolerance, viewer, and plotter files).
These configurations are dumped into JSON files.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import os.path
import json
from examples import examples_config

# get config
PATH_ROOT = examples_config.PATH_ROOT


def _get_plot_options(name):
    """
    The plot options are controlling the 3D wireframe rendering.
    This structure is used by the viewer and the plotter.
    """

    plot_options = {
        "title": name,  # name displayed on the window corner
        "grid_plot": True,  # plot (or not) the complete voxel geometry as wireframe
        "grid_thickness": 1.0,  # line thickness for the complete voxel geometry
        "grid_color": "black",  # line opacity for the complete voxel geometry
        "grid_opacity": 0.1,  # line color for the complete voxel geometry
        "geom_plot": True,  # plot (or not) the non-empty voxels as wireframe
        "geom_thickness": 1.0,  # line thickness for the non-empty voxels
        "geom_color": "black",  # line color for the non-empty voxels
        "geom_opacity": 0.5,  # line opacity for the non-empty voxels
        "cloud_plot": True,  # plot (or not) the provided point cloud as dots
        "cloud_color": "red",  # color of the point cloud dots
        "cloud_size": 5.0,  # size of the point cloud dots
        "cloud_opacity": 0.5,  # opacity of the point cloud dots
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
        "window_size": (800, 600),  # initial window size
    }

    return data_window


def _get_data_plotter_geometry(name):
    """
    Plot options for the material description.
    The result is plotted on the voxel structure.
    This structure is used by the plotter.
    """

    data_options = {
        "color_electric": "darkorange",
        "color_magnetic": "gainsboro",
        "color_current_source": "forestgreen",
        "color_voltage_source": "royalblue",
    }

    data = _get_data_plotter_pyvista("material", data_options, name)

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
        "color_lim": (None, None),  # clamping range for the color axis (None for complete range)
        "filter_lim": (None, None),  # hide voxels/points with values outside this range (None for complete range)
        "point_size": 10.0,  # size of the marker used for plotting on the point cloud
        "legend": "%s [%s]" % (name, unit),  # legend of the color axis
    }

    data = _get_data_plotter_pyvista("scalar_" + plot_geom, data_options, name)

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
        "color_lim": (None, None),  # clamping range for the color axis (None for complete range)
        "filter_lim": (None, None),  # hide arrows with scalar values outside this range (None for complete range)
        "arrow_threshold": 1e-3,  # relative threshold for arrows with small scalar values
        "arrow_scale": 0.75,  # relative arrow length (with respect to the voxel size)
        "legend": "%s [%s]" % (name, unit),  # legend of the color axis
    }

    data = _get_data_plotter_pyvista("arrow_" + plot_geom, data_options, name)

    return data


def _get_data_plotter_pyvista(plot_type, data_options, name):
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


def _get_data_plotter_matplotlib(data_plot, name):
    """
    Get the options defining a single Matplotlib plot.
    This structure is used by the plotter.
    """

    data = {
        "plot_framework": "matplotlib",
        "data_window": _get_data_window(name),
        "data_plot": data_plot,
        }

    return data


def get_data_tolerance():
    """
    Get the numerical options for the solver.
    This dict is used by the solver.
    """

    # iterative solver options
    solver_options = {
        "tolerance": 1e-6,  # tolerance for checking the solution residuum
        "gmres_options": {  # options for the GMRES iterative solver
            "rel_tol": 1e-6,  # relative preconditioned tolerance for GMRES stopping
            "abs_tol": 1e-12,  # absolute preconditioned tolerance for GMRES stopping
            "n_between_restart": 20,  # number of GMRES iterations between restarts
            "n_maximum_restart": 100,  # maximum number of GMRES restart
        }
    }

    # matrix condition check options
    condition_options = {
        "check": True,  # check (or not) the condition number of the matrices
        "tolerance": 1e15,  # maximum allowable condition number for the matrices
        "norm_options": {  # options for computing the one-norm estimate
            "t_accuracy": 2,  # accuracy parameter for the one-norm estimate
            "n_iter_max": 25,  # maximum number of iterations for the one-norm estimate
        }
    }

    # control where numerical approximations are used for the Green anc coupling functions
    #   - if the normalized voxel distance is smaller than the threshold, analytical solutions are used
    #   - if the normalized voxel distance is larger than the threshold, numerical approximations are used
    green_simplify = 20.0
    coupling_simplify = 20.0

    # assemble the data
    data_tolerance = {
        "green_simplify": green_simplify,
        "coupling_simplify": coupling_simplify,
        "solver_options": solver_options,
        "condition_options": condition_options,
    }

    return data_tolerance


def get_data_viewer():
    """
    Get the options for visualizing the voxel structure.
    Each element in the list represents a different plot.
    This list is used by the viewer.
    """

    data_viewer = [
        {
            "data_window": _get_data_window("Domain"),
            "data_plot": {
                "plot_type": "domain",
                "data_options": {
                    "colormap": "Accent",
                    "opacity": 1.0,
                },
                "clip_options": _get_clip_options(),
                "plot_options": _get_plot_options("Domain"),
            }
        },
        {
            "data_window": _get_data_window("Connection"),
            "data_plot": {
                "plot_type": "connection",
                "data_options": {
                    "colormap": "Accent",
                    "opacity": 1.0,
                },
                "clip_options": _get_clip_options(),
                "plot_options": _get_plot_options("Connection"),
            }
        },
        {
            "data_window": _get_data_window("Tolerance"),
            "data_plot": {
                "plot_type": "tolerance",
                "data_options": {
                    "color_voxel": "red",
                    "color_reference": "blue",
                    "opacity_voxel": 0.5,
                    "opacity_reference": 0.5,
                },
                "clip_options": _get_clip_options(),
                "plot_options": _get_plot_options("Connection"),
            }
        },
    ]

    return data_viewer


def get_data_plotter():
    """
    Get the options for plotting the solver solution.
    Each element in the list represents a different plot.
    This list is used by the plotter.
    """

    # get the plots
    data_plotter = [
        _get_data_plotter_geometry("Material"),
        _get_data_plotter_scalar("voxel", "V_c_abs", 1e0, "V", "El. Potential"),
        _get_data_plotter_scalar("voxel", "V_m_abs", 1e0, "A", "Mag. Potential"),
        _get_data_plotter_scalar("voxel", "S_c_abs", 1e-9, "A/mm3", "El. Source"),
        _get_data_plotter_scalar("voxel", "Q_m_abs", 1e0, "mT/mm", "Mag. Source"),
        _get_data_plotter_scalar("voxel", "P_c_abs", 1e-6, "W/cm3", "El. Losses"),
        _get_data_plotter_scalar("voxel", "P_m_abs", 1e-6, "W/cm3", "Mag. Losses"),
        _get_data_plotter_scalar("voxel", "J_c_norm_abs", 1e-6, "A/mm2", "Current"),
        _get_data_plotter_arrow("voxel", "J_c_norm_re", "J_c_vec_re", 1e-6, "A/mm2", "Re. Current"),
        _get_data_plotter_arrow("voxel", "J_c_norm_im", "J_c_vec_im", 1e-6, "A/mm2", "Im. Current"),
        _get_data_plotter_scalar("voxel", "B_m_norm_abs", 1e3, "mT", "Flux Density"),
        _get_data_plotter_arrow("voxel", "B_m_norm_re", "B_m_vec_re", 1e3, "mT", "Re. Flux Density"),
        _get_data_plotter_arrow("voxel", "B_m_norm_im", "B_m_vec_im", 1e3, "mT", "Im. Flux Density"),
        _get_data_plotter_scalar("point", "H_norm_abs", 1e0, "A/m", "Mag. Field Norm"),
        _get_data_plotter_arrow("point", "H_norm_re", "H_vec_re", 1e0, "A/m", "Re. Mag. Field"),
        _get_data_plotter_arrow("point", "H_norm_im", "H_vec_im", 1e0, "A/m", "Im. Mag. Field"),
        _get_data_plotter_matplotlib("convergence", "Convergence"),
        _get_data_plotter_matplotlib("residuum", "Residuum"),
    ]

    return data_plotter


if __name__ == "__main__":
    # get the filename
    file_tolerance = os.path.join(PATH_ROOT, "config", "tolerance.json")
    file_plotter = os.path.join(PATH_ROOT, "config", "plotter.json")
    file_viewer = os.path.join(PATH_ROOT, "config", "viewer.json")

    # get data
    data_tolerance = get_data_tolerance()
    data_viewer = get_data_viewer()
    data_plotter = get_data_plotter()

    # create file
    with open(file_tolerance, "w") as fid:
        json.dump(data_tolerance, fid, indent=4)
    with open(file_viewer, "w") as fid:
        json.dump(data_viewer, fid, indent=4)
    with open(file_plotter, "w") as fid:
        json.dump(data_plotter, fid, indent=4)
