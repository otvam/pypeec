"""
Different functions for plotting results with Matplotlib.

For the viewer, the following plots are available:
    - A matrix showing which domains are adjacent to each others.
    - A matrix showing which domains are connected to each others.

For the plotter, the following plots are available:
    - A plot describing the convergence of the matrix solver.
    - A histogram describing the residuum of the solution.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as col


def _get_plot_residuum(fig, residuum, data_plot):
    """
    Plot the final residuum (absolute value) with a histogram.
    """

    # extract the data
    title = data_plot["title"]
    n_bins = data_plot["n_bins"]
    tol_bins = data_plot["tol_bins"]
    color_bar = data_plot["color_bar"]
    color_edge = data_plot["color_edge"]

    # activate the figure
    plt.figure(fig)

    # get absolute value
    residuum = np.abs(residuum)

    # clamp small and large values
    v_min = np.finfo(residuum.dtype).eps
    v_max = np.finfo(residuum.dtype).max
    residuum = np.clip(residuum, v_min, v_max)

    # get the bins
    v_min = np.min(residuum) / (1 + tol_bins)
    v_max = np.max(residuum) * (1 + tol_bins)
    bins = np.logspace(np.log10(v_min), np.log10(v_max), n_bins)

    # plot the histogram
    plt.hist(residuum, bins=bins, edgecolor=color_edge, color=color_bar)

    # get log axis
    plt.xscale("log")
    plt.yscale("log")

    # add cosmetics
    plt.grid()
    plt.xlabel("residuum (a.u.)")
    plt.ylabel("counts (a.u.)")
    if title is not None:
        plt.title(title)


def _get_plot_convergence(fig, power_init, power_final, power_vec, data_plot):
    """
    Plot the convergence of the iterative matrix solver.
    """

    # extract the data
    title = data_plot["title"]
    color_active = data_plot["color_active"]
    color_reactive = data_plot["color_reactive"]
    marker = data_plot["marker"]
    width = data_plot["width"]

    # activate the figure
    plt.figure(fig)

    # get convergence
    power_vec = np.concatenate(([power_init], power_vec))
    error_vec = (power_vec - power_final) / np.abs(power_final)
    real_vec = np.abs(np.real(error_vec))
    imag_vec = np.abs(np.imag(error_vec))

    # clamp small and large values
    v_min = np.finfo(error_vec.dtype).eps
    v_max = np.finfo(error_vec.dtype).max
    real_vec = np.clip(real_vec, v_min, v_max)
    imag_vec = np.clip(imag_vec, v_min, v_max)

    # plot the data
    plt.plot(real_vec, "-o", color=color_active, markersize=marker, linewidth=width, label="P")
    plt.plot(imag_vec, "-o", color=color_reactive, markersize=marker, linewidth=width, label="Q")

    # get log axis
    plt.yscale("log")

    # add cosmetics
    plt.grid()
    plt.legend()
    plt.xlabel("iterations (#)")
    plt.ylabel("convergence (a.u.)")
    if title is not None:
        plt.title(title)


def _get_plot_matrix(fig, tag_list, mat, data_plot):
    """
    Plot the domain connections.
    """

    # extract the data
    title = data_plot["title"]
    width = data_plot["width"]
    color_edge = data_plot["color_edge"]
    color_true = data_plot["color_true"]
    color_false = data_plot["color_false"]

    # position vector and color matrix
    inv = np.invert(mat)
    vec = np.arange(len(tag_list))
    mesh = np.full((len(tag_list), len(tag_list), 3), np.nan, dtype=np.float64)
    mesh[mat, :] = col.to_rgb(color_true)
    mesh[inv, :] = col.to_rgb(color_false)

    # activate the figure
    plt.figure(fig)

    # plot the matrix
    plt.pcolormesh(vec, vec, mesh, edgecolors=color_edge, linewidth=width)

    # add cosmetics
    plt.xticks(ticks=vec, labels=tag_list)
    plt.yticks(ticks=vec, labels=tag_list)
    if title is not None:
        plt.title(title)


def get_plot_plotter(fig, solver_convergence, layout, data_plot, data_options):
    """
    Plot the solver status (for the plotter).
    """

    # extract the data
    style = data_options["style"]
    legend = data_options["legend"]
    font = data_options["font"]

    # extract the data
    residuum = solver_convergence["residuum"]
    power_init = solver_convergence["power_init"]
    power_final = solver_convergence["power_final"]
    power_vec = solver_convergence["power_vec"]

    # plot parameters
    param = {"font.size": font, "legend.loc": legend}

    # get the main plot
    with plt.style.context(style):
        with plt.rc_context(param):
            if layout == "convergence":
                _get_plot_convergence(fig, power_init, power_final, power_vec, data_plot)
            elif layout == "residuum":
                _get_plot_residuum(fig, residuum, data_plot)
            else:
                raise ValueError("invalid plot layout")


def get_plot_viewer(fig, connect_def, layout, data_plot, data_options):
    """
    Plot a matrix with the connected/adjacent domains (for the viewer).
    """

    # extract the data
    style = data_options["style"]
    legend = data_options["legend"]
    font = data_options["font"]

    # extract the data
    tag_list = connect_def["tag_list"]
    connected_mat = connect_def["connected_mat"]
    adjacent_mat = connect_def["adjacent_mat"]

    # plot parameters
    param = {"font.size": font, "legend.loc": legend}

    # get the main plot
    with plt.style.context(style):
        with plt.rc_context(param):
            if layout == "connected":
                _get_plot_matrix(fig, tag_list, connected_mat, data_plot)
            elif layout == "adjacent":
                _get_plot_matrix(fig, tag_list, adjacent_mat, data_plot)
            else:
                raise ValueError("invalid plot layout")
