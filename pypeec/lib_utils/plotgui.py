"""
Module for managing plotting windows with PyVista and Matplotlib.
The Qt framework or Jupyter are used for showing the plots.

WARNING: This module is using different more or less dirty hacks.
         This module is likely to be non-portable across platforms (tested on Linux x64).
         This module is likely to break with newer/older versions of the dependencies.

TODO: Making many plots can lead to segmentation fault with PyVista.
      Not sure if the problem lies with PyPEEC, PyVista, PyVistaQt or Vtk.

TODO: A delay is adding between the plots when using the Qt framework.
      This is a dirty workaround for a race condition in PyVista/PyVistaQt.

TODO: Quitting or making screenshot might cause a crash of PyVista.
      The reason is that the rendering is not forced properly with multiple windows.
      A workaround is to patch the PyVista to force a rendering before screenshots.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import os
import sys
import ctypes
import signal
import time
import importlib.resources
import pyvista
import pyvistaqt
import matplotlib
import matplotlib.pyplot
import qtpy.QtWidgets
import qtpy.QtGui
from pypeec.lib_utils import timelogger
from pypeec import config

# get a logger
LOGGER = timelogger.get_logger("PLOTGUI")

# get config
PAUSE_GUI = config.PAUSE_GUI


class PlotGui:
    """
    Manage PyVista and Matplotlib plots.
    Three different plot mode are available:
        - qt: show plot windows with the Qt framework
        - nb: show the plot inside a Jupyter notebook
        - silent: close all the plots without showing them
    """

    def __init__(self, is_silent):
        """
        Constructor.
        Init the plots.
        """

        # assign variable
        self.pl_list = []
        self.fig_list = []

        # find the plot mode
        is_notebook = self._get_notebook()
        if is_silent:
            self.plot_mode = "nop"
        else:
            if is_notebook:
                self.plot_mode = "nb"
            else:
                self.plot_mode = "qt"

        # create the Qt App
        if self.plot_mode == "qt":
            self.app = qtpy.QtWidgets.QApplication([])
        else:
            self.app = None

        # set the app ID in order to get a consistent icon on MS Windows
        if (self.plot_mode == "qt") and (os.name == "nt"):
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("pypeec")

        # setup PyVista and Matplotlib
        if self.plot_mode == "qt":
            pyvista.set_plot_theme("default")
            matplotlib.use("QtAgg")
        if self.plot_mode == "nb":
            pyvista.set_plot_theme("default")
            pyvista.set_jupyter_backend("trame")

    @staticmethod
    def _get_notebook():
        """
        Check if the code is executed inside a Jupyter notebook.
        """

        try:
            import IPython
            res = IPython.get_ipython()
            if res is not None:
                return True
            else:
                return False
        except ImportError:
            return False

    @staticmethod
    def _get_plotter_pyvista_qt(title, show_menu, window_size):
        """
        Create a PyVista plotter for the Qt framework.
        """

        # cast window size
        if window_size is not None:
            window_size = tuple(window_size)

        # get Qt plotter
        pl = pyvistaqt.BackgroundPlotter(
            show=False,
            toolbar=show_menu,
            menu_bar=show_menu,
            title=title,
            window_size=window_size,
        )
        # set icon
        with importlib.resources.path("pypeec", "pypeec.png") as file_icon:
            pl.set_icon(str(file_icon))

        # pause to avoid race conditions
        time.sleep(PAUSE_GUI)

        return pl

    @staticmethod
    def _get_plotter_pyvista_nb(notebook_size):
        """
        Create a PyVista plotter for Jupyter notebooks.
        """

        # cast window size
        if notebook_size is not None:
            notebook_size = tuple(notebook_size)

        # create plotter
        pl = pyvista.Plotter(notebook=True, window_size=notebook_size)

        return pl

    @staticmethod
    def _get_figure_matplotlib_qt(title, show_menu, window_size):
        """
        Create a Matplotlib figure for the Qt framework.
        """

        # get the icon
        with importlib.resources.path("pypeec", "pypeec.png") as file_icon:
            res_icon = qtpy.QtGui.QIcon(str(file_icon))

        # get the figure
        fig = matplotlib.pyplot.figure(tight_layout=True)

        # set the Qt options
        man = matplotlib.pyplot.get_current_fig_manager()
        man.window.setWindowTitle(title)
        man.window.setWindowIcon(res_icon)

        # set the menu
        if show_menu:
            man.toolbar.show()
        else:
            man.toolbar.hide()

        # set window size
        if window_size is not None:
            (sx, sy) = window_size
            man.window.resize(sx, sy)

        # pause to avoid race conditions
        time.sleep(PAUSE_GUI)

        return fig

    @staticmethod
    def _get_figure_matplotlib_nb(notebook_size):
        """
        Create a Matplotlib figure for Jupyter notebooks.
        """

        # create figure
        fig = matplotlib.pyplot.figure(tight_layout=True)

        # set window size
        if notebook_size is not None:
            (sx, sy) = notebook_size
            fig.set_size_inches(sx / fig.dpi, sy / fig.dpi)

        return fig

    def open_pyvista(self, data_window):
        """
        Get a PyVista plotter.
        """

        # get the data
        title = data_window["title"]
        show_menu = data_window["show_menu"]
        window_size = data_window["window_size"]
        notebook_size = data_window["notebook_size"]

        # create the figure
        if self.plot_mode == "qt":
            pl = self._get_plotter_pyvista_qt(title, show_menu, window_size)
        elif self.plot_mode == "nb":
            pl = self._get_plotter_pyvista_nb(notebook_size)
        elif self.plot_mode == "nop":
            pl = pyvista.Plotter(off_screen=True)
        else:
            raise ValueError("invalid plot mode")

        # add the plotter to the list
        self.pl_list.append(pl)

        return pl

    def open_matplotlib(self, data_window):
        """
        Get a Matplotlib figure.
        """

        # get the data
        title = data_window["title"]
        show_menu = data_window["show_menu"]
        window_size = data_window["window_size"]
        notebook_size = data_window["notebook_size"]

        # create the figure
        if self.plot_mode == "qt":
            fig = self._get_figure_matplotlib_qt(title, show_menu, window_size)
        elif self.plot_mode == "nb":
            fig = self._get_figure_matplotlib_nb(notebook_size)
        elif self.plot_mode == "nop":
            fig = matplotlib.pyplot.figure()
        else:
            raise ValueError("invalid plot mode")

        # add the figure to the list
        self.fig_list.append(fig)

        return fig

    def show(self):
        """
        Show the plots.
        The following behavior is done for the different plot mode:
            - qt: show plot windows with the Qt framework (blocking call)
            - nb: show the plot inside a Jupyter notebook (non-blocking call)
            - nop: close all the plots without showing them (non-blocking call)
        """

        LOGGER.debug("number of PyVista plots: %s" % len(self.pl_list))
        LOGGER.debug("number of Matplotlib plots: %s" % len(self.fig_list))

        if (len(self.pl_list) == 0) and (len(self.fig_list) == 0):
            return True

        if self.plot_mode == "qt":
            LOGGER.debug("entering the plot event loop")

            # signal handler for closing all the windows
            def signal_handler(*_):
                for pl in self.pl_list:
                    pl.app_window.close()
                matplotlib.pyplot.close("all")
                sys.exit(130)

            # signal for quitting the event loop with interrupt signal
            signal.signal(signal.SIGINT, signal_handler)

            # pause to avoid race conditions
            time.sleep(PAUSE_GUI)

            # show the different plots
            for pl in self.pl_list:
                pl.app_window.show()
            matplotlib.pyplot.show(block=False)

            # enter the event loop
            exit_code = self.app.exec_()
            status = exit_code == 0

            return status
        elif self.plot_mode == "nb":
            # display the non-blocking call
            LOGGER.debug("display notebook plots")

            # show the different plots
            for pl in self.pl_list:
                pl.show(jupyter_backend='trame')
            matplotlib.pyplot.show(block=False)

            return True
        elif self.plot_mode == "nop":
            LOGGER.debug("close all the plots")

            for pl in self.pl_list:
                pl.close()
            matplotlib.pyplot.close("all")

            return True
        else:
            raise ValueError("invalid plot mode")
