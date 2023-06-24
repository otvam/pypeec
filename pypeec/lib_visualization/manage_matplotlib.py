"""
Different functions for plotting solver results with Matplotlib.

For the plotter, the following plots are available:
    - plot of the convergence of the matrix solver
    - histogram of the final residuum of the solution
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import numpy as np
import matplotlib.pyplot as plt


def _get_plot_residuum(fig, title, res, plot_content):
    """
    Plot the final residuum (absolute value) with a histogram.
    """

    # extract the data
    n_bins = plot_content["n_bins"]
    tol_bins = plot_content["tol_bins"]
    bar_color = plot_content["bar_color"]
    edge_color = plot_content["edge_color"]

    # activate the figure
    plt.figure(fig)

    # get absolute value and the log
    res_abs = np.abs(res)
    v_min = np.finfo(res_abs.dtype).eps
    v_max = np.finfo(res_abs.dtype).max
    res_abs = np.clip(res_abs, v_min, v_max)

    # counts the elements
    n_plt = len(res_abs)
    n_tot = len(res)

    # get the bins
    v_min = min(res_abs)/(1+tol_bins)
    v_max = max(res_abs)*(1+tol_bins)
    bins = np.logspace(np.log10(v_min), np.log10(v_max), n_bins)

    # plot the histogram
    plt.hist(res_abs, bins=bins, edgecolor=edge_color, color=bar_color)

    # get log axis
    plt.xscale("log")
    plt.yscale("log")

    # add cosmetics
    plt.grid()
    plt.xlabel("residuum (a.u.)")
    plt.ylabel("counts (a.u.)")
    plt.title("%s / n_tot = %d / n_plt = %d" % (title, n_tot, n_plt))


def _get_plot_convergence(fig, title, conv, plot_content):
    """
    Plot the convergence of the iterative matrix solver.
    """

    # extract the data
    color_active = plot_content["color_active"]
    color_reactive = plot_content["color_reactive"]
    marker = plot_content["marker"]

    # activate the figure
    plt.figure(fig)

    # counts
    iter_vec = conv["iter_vec"]
    P_vec = conv["P_vec"]
    Q_vec = conv["Q_vec"]

    # plot the data
    plt.plot(iter_vec, P_vec, color=color_active, marker=marker, label="P")
    plt.plot(iter_vec, Q_vec, color=color_reactive, marker=marker, label="Q")

    # add cosmetics
    plt.grid()
    plt.legend()
    plt.xlabel("iterations (#)")
    plt.ylabel("convergence (a.u.)")
    plt.title("%s / n_iter = %d" % (title, len(iter_vec)))


def get_plot_plotter(fig, title, res, conv, data_plot):
    """
    Plot the solver status (for the plotter).
    """

    # extract the data
    plot_type = data_plot["plot_type"]
    plot_content = data_plot["plot_content"]

    # get the main plot
    if plot_type == "convergence":
        _get_plot_convergence(fig, title, conv, plot_content)
    elif plot_type == "residuum":
        _get_plot_residuum(fig, title, res, plot_content)
    else:
        raise ValueError("invalid plot type and plot feature")
