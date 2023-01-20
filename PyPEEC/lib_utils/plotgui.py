"""
Module for managing plotting windows with PyVista and Matplotlib.
The Qt framework is used for the GUI.

WARNING: This module is using different more or less dirty hacks.
         This module is likely to be non-portable.
         This module is likely to break with some version of the dependencies.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import pyvistaqt as pvqt
import pyvista as pv
import matplotlib as mpl
import matplotlib.pyplot as plt
import qtpy.QtWidgets as qtw
import qtpy.QtGui as qtu
from PyPEEC import config

# get config
PATH_ROOT = config.PATH_ROOT

# set defaults for PyVista
pv.set_plot_theme('default')

# set default for Matplotlib
mpl.use('QtAgg')


def open_pyvista(data_window, is_blocking):
    """
    Get a PyVista plotter.
    If the call is non-blocking, the window is not shown.
    """

    # get the data
    title = data_window["title"]
    show_menu = data_window["show_menu"]
    size = data_window["size"]

    # create the figure (blocking or non-blocking)
    if is_blocking:
        # get Qt plotter if blocking
        pl = pvqt.BackgroundPlotter(
            show=True,
            toolbar=show_menu,
            menu_bar=show_menu,
            title=title,
            window_size=tuple(size),
        )
        # set icon
        pl.set_icon(PATH_ROOT + "/icon.png")
    else:
        # get standard plotter if non-blocking
        pl = pv.Plotter(off_screen=True)

    return pl


def open_matploblib(data_window, is_blocking):
    # get the data
    title = data_window["title"]
    show_menu = data_window["show_menu"]
    size = data_window["size"]

    # create the figure (blocking or non-blocking)
    if is_blocking:
        (fig, ax) = plt.subplots(tight_layout=True)

        # set the Qt options
        (sizex, sizey) = size
        icn = qtu.QIcon(PATH_ROOT + "/icon.png")

        man = plt.get_current_fig_manager()
        man.window.setWindowTitle(title)
        man.window.setWindowIcon(icn)
        man.window.resize(sizex, sizey)

        if show_menu:
            man.toolbar.show()
        else:
            man.toolbar.hide()
    else:
        # get a default plot is non-blocking
        (fig, ax) = plt.subplots()

    return fig


def close_pyvista(pl, is_blocking):
    """
    Close a PyVista plotter (only if the call is non-blocking).
    """

    # close plotter if non-blocking
    if not is_blocking:
        pl.close()
        pl.deep_clean()


def close_matplotlib(fig, is_blocking):
    if not is_blocking:
        plt.close(fig)


def open_app(is_blocking):
    """
    Create a master Qt app for all the plotter windows.
    """

    if is_blocking:
        app = qtw.QApplication([])
    else:
        app = None

    return app


def run_app(app, is_blocking):
    """
    Enter the event loop (only if the call is non-blocking).
    """

    if is_blocking:
        plt.show(block=False)
        exit_code = app.exec_()
        return exit_code == 0
    else:
        return True
