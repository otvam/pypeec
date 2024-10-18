"""
Module for managing plotting windows with PyVista and Matplotlib.
The Qt framework or Jupyter are used for showing the plots.

Warning
-------
    - This module is using different more or less dirty hacks.
    - This module is likely to be non-portable across platforms (tested on Linux x64).
    - This module is likely to break with newer/older versions of the dependencies.

Todo
----
    - Making many plots can lead to segmentation fault with PyVista.
    - Not sure if the problem lies with PyPEEC, PyVista, PyVistaQt, or Vtk.

Todo
----
    - Quitting or making screenshot might cause a crash of PyVista.
    - The reason is that the rendering is not forced properly with multiple windows.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import os
import sys
import ctypes
import signal
import os.path
import importlib.resources
import pyvista
import pyvistaqt
import matplotlib
import matplotlib.pyplot
import PyQt5.QtWidgets
import PyQt5.QtGui
import scilogger

# get a logger
LOGGER = scilogger.get_logger(__name__, "pypeec")


class _QApplication(object):
    """
    Singleton class for creating a single instance of the Qt application.
    """

    def __new__(cls):
        """
        Create the singleton QT application instance.
        """

        if not hasattr(cls, 'app'):
            cls.instance = super(_QApplication, cls).__new__(cls)
            cls.app = PyQt5.QtWidgets.QApplication([])

        return getattr(cls, "instance")

    def get_app(self):
        """
        Get the singleton QT application instance.
        """

        return self.app


class PlotGui:
    """
    Manage PyVista and Matplotlib plots.
    Three different plot mode are available:
        - "qt", the Qt framework is used for the rendering (default).
        - "nb", the plots are rendered within the Jupyter notebook.
        - "save", the plots are not shown but saved as screenshots.
        - "none", the plots are not shown (test mode).
    """

    def __init__(self, plot_mode, folder, name):
        """
        Constructor.
        Init the plots.
        """

        # assign variable
        self.plot_mode = plot_mode
        self.folder = folder
        self.name = name
        self.pl_list = []
        self.fig_list = []

        # create the Qt App
        if self.plot_mode == "qt":
            self.app = _QApplication().get_app()
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
        with importlib.resources.path("pypeec.data", "pypeec.png") as file:
            pl.set_icon(str(file))

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
    def _get_plotter_pyvista_nop(image_size):
        """
        Create a PyVista plotter for silent rendering.
        """

        # cast window size
        if image_size is not None:
            image_size = tuple(image_size)

        # create plotter
        pl = pyvista.Plotter(off_screen=True, window_size=image_size)

        return pl

    @staticmethod
    def _get_figure_matplotlib_qt(title, show_menu, window_size):
        """
        Create a Matplotlib figure for the Qt framework.
        """

        # get the icon
        with importlib.resources.path("pypeec.data", "pypeec.png") as file:
            res_icon = PyQt5.QtGui.QIcon(str(file))

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
            fig.set_size_inches(sx/fig.dpi, sy/fig.dpi)

        return fig

    @staticmethod
    def _get_figure_matplotlib_nop(image_size):
        """
        Create a Matplotlib figure for silent rendering.
        """

        # create figure
        fig = matplotlib.pyplot.figure(tight_layout=True)

        # set window size
        if image_size is not None:
            (sx, sy) = image_size
            fig.set_size_inches(sx/fig.dpi, sy/fig.dpi)

        return fig

    def _show_figure_qt(self):
        """
        Show all the figures (Qt framework).
        """

        # signal handler for closing all the windows
        def signal_handler(*_):
            for tag, pl in self.pl_list:
                pl.app_window.close()
            matplotlib.pyplot.close("all")
            sys.exit(130)

        # signal for quitting the event loop with interrupt signal
        signal.signal(signal.SIGINT, signal_handler)

        # show the different PyVista plots
        for tag, pl in self.pl_list:
            pl.app_window.show()

        # show the different Matplotlib plots
        matplotlib.pyplot.show(block=False)

        # enter the event loop
        exit_code = self.app.exec()

        # quit app
        self.app.quit()

        # check status
        if exit_code != 0:
            RuntimeError("error during the Qt event loop / exit_code = %d" % exit_code)

    def _show_figure_nb(self):
        """
        Show all the figures (Jupyter notebooks)
        """

        # show the different PyVista plots
        for tag, pl in self.pl_list:
            pl.show(jupyter_backend='trame')

        # show the different Matplotlib plots
        matplotlib.pyplot.show(block=False)

    def _show_figure_nop(self):
        """
        Show all the figures (silent rendering)
        """

        # close the different PyVista plots
        for tag, pl in self.pl_list:
            pl.close()

        # close the different Matplotlib plots
        matplotlib.pyplot.close("all")

    def _get_filename(self, tag):
        """
        Get the plot filenames.
        """

        filename = "%s.png" % tag
        if self.name:
            filename = "%s_%s" % (self.name, filename)
        if self.folder:
            filename = os.path.join(self.folder, filename)

        return filename

    def _save_screenshot(self):
        """
        Save all the plots as images.
        """

        # save the PyVista plots
        for tag, pl in self.pl_list:
            filename = self._get_filename(tag)
            pl.screenshot(filename)

        # save the Matplotlib plots
        for tag, fig in self.fig_list:
            filename = self._get_filename(tag)
            fig.savefig(filename)

    def open_pyvista(self, tag, title, data_window):
        """
        Get a PyVista plotter.
        """

        # extract the data
        show_menu = data_window["show_menu"]
        image_size = data_window["image_size"]
        window_size = data_window["window_size"]
        notebook_size = data_window["notebook_size"]

        # prepend tag
        title = tag + " / " + title

        # create the figure
        if self.plot_mode == "qt":
            pl = self._get_plotter_pyvista_qt(title, show_menu, window_size)
        elif self.plot_mode == "nb":
            pl = self._get_plotter_pyvista_nb(notebook_size)
        elif self.plot_mode in ["save", "none"]:
            pl = self._get_plotter_pyvista_nop(image_size)
        else:
            raise ValueError("invalid plot mode")

        # add the plotter to the list
        self.pl_list.append((tag, pl))

        return pl

    def open_matplotlib(self, tag, title, data_window):
        """
        Get a Matplotlib figure.
        """

        # extract the data
        show_menu = data_window["show_menu"]
        image_size = data_window["image_size"]
        window_size = data_window["window_size"]
        notebook_size = data_window["notebook_size"]

        # prepend tag
        title = tag + " / " + title

        # create the figure
        if self.plot_mode == "qt":
            fig = self._get_figure_matplotlib_qt(title, show_menu, window_size)
        elif self.plot_mode == "nb":
            fig = self._get_figure_matplotlib_nb(notebook_size)
        elif self.plot_mode in ["save", "none"]:
            fig = self._get_figure_matplotlib_nop(image_size)
        else:
            raise ValueError("invalid plot mode")

        # add the figure to the list
        self.fig_list.append((tag, fig))

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
            return

        if self.plot_mode == "qt":
            LOGGER.debug("entering the plot event loop")
            self._show_figure_qt()
            LOGGER.debug("exiting the plot event loop")
        elif self.plot_mode == "nb":
            LOGGER.debug("display notebook plots")
            self._show_figure_nb()
            LOGGER.debug("exit plotting routine")
        elif self.plot_mode == "save":
            LOGGER.debug("save and close all the plots")
            self._save_screenshot()
            self._show_figure_nop()
            LOGGER.debug("exit plotting routine")
        elif self.plot_mode == "none":
            LOGGER.debug("close all the plots")
            self._show_figure_nop()
            LOGGER.debug("exit plotting routine")
        else:
            raise ValueError("invalid plot mode")
