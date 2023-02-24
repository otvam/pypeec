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


def _get_plot_residuum(fig, res_all, data_options):
    """
    Plot the final residuum (absolute value) with a histogram.
    """

    # get the data
    n_bins = data_options["n_bins"]
    bar_color = data_options["bar_color"]
    edge_color = data_options["edge_color"]

    # activate the figure
    plt.figure(fig)

    # get absolute value and the log
    res_abs = np.abs(res_all)
    v_min = np.finfo(res_abs.dtype).eps
    v_max = np.finfo(res_abs.dtype).max
    res_abs = np.clip(res_abs, v_min, v_max)
    res_log = np.log10(res_abs)

    # counts the elements
    n_tot = len(res_all)
    n_plt = len(res_abs)

    # get the bins
    bins = np.logspace(min(res_log), max(res_log), n_bins)
    bins[0] = min(res_abs)
    bins[-1] = max(res_abs)

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


def _get_plot_convergence(fig, res_iter, data_options):
    """
    Plot the convergence of the iterative matrix solver.
    """

    # get the data
    color = data_options["color"]
    marker = data_options["marker"]

    # activate the figure
    plt.figure(fig)

    # counts
    n_iter = len(res_iter)

    # plot the data
    idx_iter = np.arange(1, n_iter+1)
    plt.semilogy(idx_iter, res_iter, color=color, marker=marker)

    # add cosmetics
    plt.grid()
    plt.xlabel("iterations (#)")
    plt.ylabel("residuum (a.u.)")
    plt.title("Solver Convergence / n_iter = %d" % n_iter)


def get_plot_plotter(fig, solver_status, data_plot):
    """
    Plot the solver status (for the plotter).
    """

    # get the data
    plot_type = data_plot["plot_type"]
    data_options = data_plot["data_options"]

    # get the data
    res_all = solver_status["res_all"]
    res_iter = solver_status["res_iter"]

    # get the main plot
    if plot_type == "convergence":
        _get_plot_convergence(fig, res_iter, data_options)
    elif plot_type == "residuum":
        _get_plot_residuum(fig, res_all, data_options)
    else:
        raise ValueError("invalid plot type and plot feature")
