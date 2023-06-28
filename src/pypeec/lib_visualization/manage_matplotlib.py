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


def _get_plot_residuum(fig, res, data_plot):
    """
    Plot the final residuum (absolute value) with a histogram.
    """

    # extract the data
    n_bins = data_plot["n_bins"]
    tol_bins = data_plot["tol_bins"]
    bar_color = data_plot["bar_color"]
    edge_color = data_plot["edge_color"]

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
    plt.title("Solver Residuum / n_tot = %d / n_plt = %d" % (n_tot, n_plt))


def _get_plot_convergence(fig, conv, data_plot):
    """
    Plot the convergence of the iterative matrix solver.
    """

    # extract the data
    color_active = data_plot["color_active"]
    color_reactive = data_plot["color_reactive"]
    marker = data_plot["marker"]
    width = data_plot["width"]

    # activate the figure
    plt.figure(fig)

    # counts
    iter_vec = conv["iter_vec"]
    P_vec = conv["P_vec"]
    Q_vec = conv["Q_vec"]

    # plot the data
    plt.plot(iter_vec, P_vec, "-o", color=color_active, markersize=marker, linewidth=width, label="P")
    plt.plot(iter_vec, Q_vec, "-o", color=color_reactive, markersize=marker, linewidth=width, label="Q")

    # add cosmetics
    plt.grid()
    plt.legend()
    plt.xlabel("iterations (#)")
    plt.ylabel("convergence (a.u.)")
    plt.title("Solver Convergence / n_iter = %d" % len(iter_vec))


def get_plot_plotter(fig, res, conv, format, data_plot, data_options):
    """
    Plot the solver status (for the plotter).
    """

    # extract the data
    style = data_options["style"]
    legend = data_options["legend"]
    font = data_options["font"]

    # plot parameters
    param = {"font.size": font, "legend.loc": legend}

    # get the main plot
    with plt.style.context(style):
        with plt.rc_context(param):
            if format == "convergence":
                _get_plot_convergence(fig, conv, data_plot)
            elif format == "residuum":
                _get_plot_residuum(fig, res, data_plot)
            else:
                raise ValueError("invalid plot type and plot feature")
