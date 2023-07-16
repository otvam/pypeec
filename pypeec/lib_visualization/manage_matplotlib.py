"""
Different functions for plotting solver results with Matplotlib.

For the plotter, the following plots are available:
    - plot of the convergence of the matrix solver
    - histogram of the final residuum of the solution
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

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

    # get rms
    n_dof = len(res)
    res_rms = np.sqrt(np.mean(np.abs(res)**2))

    # get absolute value
    res_abs = np.abs(res)

    # clamp small and large values
    v_min = np.finfo(res_abs.dtype).eps
    v_max = np.finfo(res_abs.dtype).max
    res_abs = np.clip(res_abs, v_min, v_max)

    # get the bins
    v_min = np.min(res_abs)/(1+tol_bins)
    v_max = np.max(res_abs)*(1+tol_bins)
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
    plt.title("Residuum / n_dof = %d / res_rms = %.2e" % (n_dof, res_rms))


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
    power_vec = conv["power_vec"]

    # get final iteration
    iter_final = iter_vec[-1]
    power_final = power_vec[-1]

    # get convergence
    iter_vec = iter_vec[0:-1]
    power_vec = (power_vec[0:-1]-power_final)/np.abs(power_final)
    real_vec = np.abs(np.real(power_vec))
    imag_vec = np.abs(np.imag(power_vec))

    # plot the data
    plt.plot(iter_vec, real_vec, "-o", color=color_active, markersize=marker, linewidth=width, label="P")
    plt.plot(iter_vec, imag_vec, "-o", color=color_reactive, markersize=marker, linewidth=width, label="Q")

    # get log axis
    plt.yscale("log")

    # add cosmetics
    plt.grid()
    plt.legend()
    plt.xlabel("iterations (#)")
    plt.ylabel("convergence (a.u.)")
    plt.title(f"Convergence: iter = {iter_final:d} / S = {power_final:.2e} VA")


def get_plot_plotter(fig, res, conv, layout, data_plot, data_options):
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
            if layout == "convergence":
                _get_plot_convergence(fig, conv, data_plot)
            elif layout == "residuum":
                _get_plot_residuum(fig, res, data_plot)
            else:
                raise ValueError("invalid plot type and plot feature")
