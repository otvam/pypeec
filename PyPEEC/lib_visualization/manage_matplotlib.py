"""
Different functions for plotting solver results with Matplotlib.

For the plotter, the following plots are available:
    - plot of the convergence of the matrix solver
    - histogram of the final residuum of the solution
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np
import matplotlib.pyplot as plt


def _get_plot_residuum(fig, res_all):
    """
    Plot the final residuum (absolute value) with a histogram.
    """

    # activate the figure
    plt.figure(fig)

    # get absolute value and the log
    res_abs = np.abs(res_all)
    v_min = np.finfo(res_abs.dtype).eps
    v_max = np.finfo(res_abs.dtype).max
    res_abs = np.clip(res_abs, v_min, v_max)
    res_log = np.log10(res_abs)

    # plot the histogram
    (hist, bins) = np.histogram(res_log)
    bins = np.power(10.0, bins)
    plt.hist(res_abs, bins=bins, edgecolor="black")

    # get log axis
    plt.xscale('log')
    plt.yscale('log', nonpositive='clip')

    # add cosmetics
    plt.grid()
    plt.xlabel('residuum (a.u.)')
    plt.ylabel('counts (a.u.)')
    plt.title("Solver Residuum")


def _get_plot_convergence(fig, res_iter):
    """
    Plot the convergence of the iterative matrix solver.
    """

    # activate the figure
    plt.figure(fig)

    # plot the data
    idx_iter = np.arange(1, len(res_iter)+1)
    plt.semilogy(idx_iter, res_iter, 'rs-')

    # add cosmetics
    plt.grid()
    plt.xlabel('iterations (#)')
    plt.ylabel('residuum (a.u.)')
    plt.title("Solver Convergence")


def get_plot_plotter(fig, solver_status, data_plot):
    """
    Plot the solver status (for the plotter).
    """

    # get the data
    res_all = solver_status["res_all"]
    res_iter = solver_status["res_iter"]

    # get the main plot
    if data_plot == "convergence":
        _get_plot_convergence(fig, res_iter)
    elif data_plot == "residuum":
        _get_plot_residuum(fig, res_all)
    else:
        raise ValueError("invalid plot type and plot feature")
