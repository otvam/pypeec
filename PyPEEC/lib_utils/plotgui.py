"""
Module for managing plotting windows with PyVista and Matplotlib.
The Qt framework is used for the GUI.

WARNING: This module is using different more or less dirty hacks.
         This module is likely to be non-portable across platforms (tested on Linux x64).
         This module is likely to break with newer/older versions of the dependencies.

WARNING: Making many plots can lead to segmentation fault with PyVista.
         Not sure if the problem lies with PyPEEC, PyVista or Vtk.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import importlib.resources
import signal
import pyvista
import pyvistaqt
import matplotlib
import matplotlib.pyplot
import qtpy.QtWidgets
import qtpy.QtGui

# set defaults for PyVista
pyvista.set_plot_theme("default")

# set default for Matplotlib
matplotlib.use("QtAgg")


def open_pyvista(data_window, is_interactive):
    """
    Get a PyVista plotter.
    If the mode is set to interactive, the plotter is customized (title, size, and menu).
    If the mode is set to non-interactive, a basic plotter is returned.
    """

    # get the data
    title = data_window["title"]
    show_menu = data_window["show_menu"]
    window_size = data_window["window_size"]

    # create the figure
    if is_interactive:
        # get Qt plotter if interactive
        pl = pyvistaqt.BackgroundPlotter(
            show=True,
            toolbar=show_menu,
            menu_bar=show_menu,
            title=title,
            window_size=tuple(window_size),
        )
        # set icon
        path_icon = importlib.resources.files("PyPEEC").joinpath("pypeec.png")
        pl.set_icon(str(path_icon))
    else:
        # get standard plotter if non-interactive
        pl = pyvista.Plotter(off_screen=True)

    return pl


def open_matplotlib(data_window, is_interactive):
    """
    Get a Matplotlib figure.
    If the mode is set to interactive, the figure is customized (title, size, and menu).
    If the mode is set to non-interactive, a basic figure is returned.
    """

    # get the data
    title = data_window["title"]
    show_menu = data_window["show_menu"]
    window_size = data_window["window_size"]

    # get the figure
    (fig, ax) = matplotlib.pyplot.subplots(tight_layout=True)

    # create the figure
    if is_interactive:
        # get the window size
        (sx, sy) = window_size

        # get the icon
        path_icon = importlib.resources.files("PyPEEC").joinpath("pypeec.png")
        icn = qtpy.QtGui.QIcon(str(path_icon))

        # set the Qt options
        man = matplotlib.pyplot.get_current_fig_manager()
        man.window.setWindowTitle(title)
        man.window.setWindowIcon(icn)
        man.window.resize(sx, sy)
        if show_menu:
            man.toolbar.show()
        else:
            man.toolbar.hide()

    return fig


def close_pyvista(pl, is_interactive):
    """
    Close a PyVista plotter (only if the mode is set to non-interactive).
    """

    if not is_interactive:
        pl.close()
        pl.deep_clean()


def close_matplotlib(fig, is_interactive):
    """
    Draw a Matplotlib figure (only if the mode is set to interactive)
    Close a Matplotlib figure (only if the mode is set to non-interactive).
    """

    if not is_interactive:
        matplotlib.pyplot.close(fig)
    else:
        gcf = matplotlib.pyplot.gcf()
        gcf.canvas.draw()
        gcf.canvas.flush_events()
        matplotlib.pyplot.show(block=False)
        gcf.canvas.flush_events()


def open_app(is_interactive):
    """
    Create a master Qt app for all the GUI windows (only if the mode is set to interactive).
    """

    if is_interactive:
        app = qtpy.QtWidgets.QApplication([])
    else:
        app = None

    return app


def run_app(app, is_interactive):
    """
    Enter the event loop (only if the mode is set to interactive).
    This will create a blocking call until all the windows are closed.
    """

    if is_interactive:
        # signal for quitting the event loop with interrupt signal
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        # enter the event loop
        exit_code = app.exec_()
        return exit_code == 0
    else:
        return True
