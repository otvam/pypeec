"""
Module for managing plotting windows with PyVista and Qt.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import os
import pyvistaqt as pvqt
from qtpy.QtWidgets import QApplication
from PyPEEC import config

# get config
PATH_ROOT = config.PATH_ROOT


def open_plotter(window_title, window_size, is_blocking):
    """
    Get a PyVista plotter.
    If the call is non-blocking, the window is not shown.
    """

    # get the plotter (with the Qt framework)
    pl = pvqt.BackgroundPlotter(
        show=is_blocking,
        toolbar=False,
        menu_bar=False,
        title=window_title,
        window_size=tuple(window_size),
    )

    # set icon
    pl.set_icon(PATH_ROOT + "/icon.png")

    return pl


def close_plotter(pl, is_blocking):
    """
    Close a PyVista plotter (only if the call is non-blocking).
    """

    # close plotter is non blocking
    if not is_blocking:
        pl.close()


def open_app(is_blocking):
    """
    Create a master Qt app for all the plotter windows.
    """

    if is_blocking:
        app = QApplication([])
    else:
        app = None

    return app


def run_app(app, is_blocking):
    """
    Enter the event loop (only if the call is non-blocking).
    """

    if is_blocking:
        exit_code = app.exec_()
        return exit_code == 0
    else:
        return True
