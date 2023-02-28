"""
Module for managing plotting windows with PyVista and Matplotlib.
The Qt framework or Jupyter are used for showing the plots.

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
from pypeec.lib_utils import timelogger

# get a logger
logger = timelogger.get_logger("PLOTGUI")


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

        # get Qt plotter if interactive
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

        return pl

    @staticmethod
    def _get_figure_matplotlib_qt(title, show_menu, sx, sy):
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
        man.window.resize(sx, sy)
        if show_menu:
            man.toolbar.show()
        else:
            man.toolbar.hide()

        return fig

    def open_pyvista(self, data_window):
        """
        Get a PyVista plotter.
        """

        # get the data
        title = data_window["title"]
        show_menu = data_window["show_menu"]
        window_size = data_window["window_size"]

        # cast window size
        window_size = tuple(window_size)

        # create the figure
        if self.plot_mode == "qt":
            pl = self._get_plotter_pyvista_qt(title, show_menu, window_size)
        elif self.plot_mode == "nb":
            pl = pyvista.Plotter(notebook=True, window_size=window_size)
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

        # get the window size
        (sx, sy) = window_size

        # create the figure
        if self.plot_mode == "qt":
            fig = self._get_figure_matplotlib_qt(title, show_menu, sx, sy)
        elif self.plot_mode == "nb":
            fig = matplotlib.pyplot.figure(tight_layout=True)
            fig.set_size_inches(sx/fig.dpi, sy/fig.dpi)
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

        logger.info("number of PyVista plots: %s" % len(self.pl_list))
        logger.info("number of Matplotlib plots: %s" % len(self.fig_list))

        if self.plot_mode == "qt":
            logger.info("entering the plot event loop")

            # signal for quitting the event loop with interrupt signal
            signal.signal(signal.SIGINT, signal.SIG_DFL)

            # show the different plots
            for pl in self.pl_list:
                pl.app_window.show()
            matplotlib.pyplot.show(block=False)

            # enter the event loop
            exit_code = self.app.exec_()

            logger.info("exiting the plot event loop")

            return exit_code == 0
        elif self.plot_mode == "nb":
            # display the non-blocking call
            logger.info("display notebook plots")

            # show the different plots
            for pl in self.pl_list:
                pl.show(jupyter_backend='trame')
            matplotlib.pyplot.show(block=False)

            return True
        elif self.plot_mode == "nop":
            logger.info("close all the plots")

            for pl in self.pl_list:
                pl.close()
            for fig in self.fig_list:
                matplotlib.pyplot.close(fig)

            return True
        else:
            raise ValueError("invalid plot mode")
