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


def _get_plot_residuum(fig, res, data_options):
    """
    Plot the final residuum (absolute value) with a histogram.
    """

    # extract the data
    n_bins = data_options["n_bins"]
    tol_bins = data_options["tol_bins"]
    bar_color = data_options["bar_color"]
    edge_color = data_options["edge_color"]

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


def _get_plot_convergence(fig, conv, data_options):
    """
    Plot the convergence of the iterative matrix solver.
    """

    # extract the data
    color = data_options["color"]
    marker = data_options["marker"]

    # activate the figure
    plt.figure(fig)

    # counts
    n_iter = len(conv)

    # plot the data
    idx_iter = np.arange(1, n_iter+1)
    plt.semilogy(idx_iter, conv, color=color, marker=marker)

    # add cosmetics
    plt.grid()
    plt.xlabel("iterations (#)")
    plt.ylabel("residuum (a.u.)")
    plt.title("Solver Convergence / n_iter = %d" % n_iter)


def get_plot_plotter(fig, res, conv, data_plot):
    """
    Plot the solver status (for the plotter).
    """

    # extract the data
    plot_type = data_plot["plot_type"]
    data_options = data_plot["data_options"]

    # get the main plot
    if plot_type == "convergence":
        _get_plot_convergence(fig, conv, data_options)
    elif plot_type == "residuum":
        _get_plot_residuum(fig, res, data_options)
    else:
        raise ValueError("invalid plot type and plot feature")
