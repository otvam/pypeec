import numpy as np
import matplotlib.pyplot as plt


def _get_plot_residuum(fig, res_raw):
    # activate the figure
    plt.figure(fig)

    # plot the data
    res_abs = np.abs(res_raw)
    plt.hist(res_abs)

    # add cosmetics
    plt.grid()
    plt.xlabel('residuum (a.u.)')
    plt.ylabel('counts (a.u.)')
    plt.title("Solver Residuum")


def _get_plot_congervence(fig, res_iter):
    # activate the figure
    plt.figure(fig)

    # plot the data
    idx_iter = np.arange(1, len(res_iter)+1)
    plt.semilogy(idx_iter, res_iter, 'sr-')

    # add cosmetics
    plt.grid()
    plt.xlabel('iterations (#)')
    plt.ylabel('residuum (a.u.)')
    plt.title("Solver Convergence")


def get_plot_plotter(fig, solver_status, data_plot):
    # get the data
    res_raw = solver_status["res_raw"]
    res_iter = solver_status["res_iter"]

    # get the main plot
    if data_plot == "convergence":
        _get_plot_congervence(fig, res_iter)
    elif data_plot == "residuum":
        _get_plot_residuum(fig, res_raw)
    else:
        raise ValueError("invalid plot type and plot feature")
