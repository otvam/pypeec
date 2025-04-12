"""
Module for managing plotting windows with PyVista and Matplotlib:
    - show the plot using the Qt framework
    - show the plots inside a Jupyter notebook
    - save the data into files (PNG images and VTK objects)
    - debug mode (do not render the plots)

The Qt-related library are only import when used.
This means that this module can run without Qt.

Warning
-------
    - This module is using different more or less dirty hacks.
    - This module is likely to be non-portable across platforms.
    - This module is likely to break with newer/older versions of the dependencies.
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
import matplotlib.pyplot
import matplotlib
import pyvista
import scilogger

# get a logger
LOGGER = scilogger.get_logger(__name__, "pypeec")

# variable for the Qt application single instance
APPQT = None


class PlotGui:
    """
    Manage PyVista and Matplotlib plots.
    """

    def __init__(self, plot_mode, folder, name):
        """
        Constructor.
        Create the Qt application.
        Set the global plot parameters.
        """

        # set the default plot mode
        if plot_mode is None:
            plot_mode = "debug"

        # set the default for the output filenames
        if name is None:
            name = "pypeec"

        # set the default for the output folder
        if folder is None:
            folder = os.getcwd()

        # assign variable
        self.plot_mode = plot_mode
        self.folder = folder
        self.name = name
        self.pl_list = []
        self.fig_list = []
        self.vtk_list = []

        # variable for the Qt application single instance
        global APPQT

        # create a single instance of the Qt App
        if (self.plot_mode == "qt") and (APPQT is None):
            # lazy import of the library
            import qtpy.QtGui
            import qtpy.QtWidgets

            # create and assign a single instance
            APPQT = qtpy.QtWidgets.QApplication(["pypeec"])
            APPQT.setApplicationDisplayName("pypeec")
            APPQT.setApplicationName("pypeec")
            APPQT.setOrganizationName("pypeec")

            # set the icon
            filename = importlib.resources.files("pypeec.data").joinpath("pypeec.png")
            res_icon = qtpy.QtGui.QIcon(str(filename))
            APPQT.setWindowIcon(res_icon)

        # set the app ID in order to get a consistent icon on MS Windows
        if (self.plot_mode == "qt") and (os.name == "nt"):
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("pypeec")

        # setup PyVista and Matplotlib
        if self.plot_mode == "qt":
            matplotlib.use("QtAgg")
        if self.plot_mode == "nb_int":
            pyvista.set_jupyter_backend("trame")
            matplotlib.use("ipympl")
        if self.plot_mode == "nb_std":
            pyvista.set_jupyter_backend("static")
            matplotlib.use("inline")

    @staticmethod
    def _get_plotter_pyvista_qt(title, show_menu, window_size):
        """
        Create a PyVista plotter for the Qt framework.
        """

        # lazy import of the library
        import pyvistaqt

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
        filename = importlib.resources.files("pypeec.data").joinpath("pypeec.png")
        pl.set_icon(str(filename))

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
    def __get_plotter_pyvista_base(image_size):
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

        # lazy import of the library
        import qtpy.QtGui

        # get the icon
        filename = importlib.resources.files("pypeec.data").joinpath("pypeec.png")
        res_icon = qtpy.QtGui.QIcon(str(filename))

        # get the figure
        with matplotlib.pyplot.ioff():
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
        with matplotlib.pyplot.ioff():
            fig = matplotlib.pyplot.figure(tight_layout=True)

        # set display options
        fig.canvas.toolbar_position = "top"
        fig.canvas.header_visible = False
        fig.canvas.footer_visible = False
        fig.canvas.resizable = False

        # set window size
        if notebook_size is not None:
            (sx, sy) = notebook_size
            fig.set_size_inches(sx / fig.dpi, sy / fig.dpi)

        return fig

    @staticmethod
    def _get_figure_matplotlib_base(image_size):
        """
        Create a Matplotlib figure for silent rendering.
        """

        # create figure
        with matplotlib.pyplot.ioff():
            fig = matplotlib.pyplot.figure(tight_layout=True)

        # set window size
        if image_size is not None:
            (sx, sy) = image_size
            fig.set_size_inches(sx / fig.dpi, sy / fig.dpi)

        return fig

    def _show_figure_qt(self):
        """
        Show all the figures (Qt framework).
        """

        # signal handler for closing all the windows
        def signal_handler(*_):
            for _, pl in self.pl_list:
                pl.app_window.close()
            matplotlib.pyplot.close("all")
            sys.exit(130)

        # signal for quitting the event loop with interrupt signal
        signal.signal(signal.SIGINT, signal_handler)

        # show the different PyVista plots
        for _, pl in self.pl_list:
            pl.app_window.show()

        # show the different Matplotlib plots
        for _, fig in self.fig_list:
            fig.show()

        # enter the event loop
        exit_code = APPQT.exec()

        # quit app
        APPQT.quit()

        # check status
        if exit_code != 0:
            RuntimeError("error during the Qt event loop / exit_code = %d" % exit_code)

    def _show_figure_nb(self, interactive):
        """
        Show all the figures (Jupyter notebooks)
        """

        # lazy import of the library
        import IPython.display

        # show the different PyVista plots
        with LOGGER.BlockIndent():
            for tag, pl in self.pl_list:
                LOGGER.debug("show / %s" % tag)
                pl.show()

        # show the different Matplotlib plots
        with LOGGER.BlockIndent():
            for tag, fig in self.fig_list:
                LOGGER.debug("show / %s" % tag)
                if interactive:
                    IPython.display.display(fig.canvas)
                else:
                    IPython.display.display(fig)

    def _close_figure(self):
        """
        Show all the figures (silent rendering)
        """

        # close the different PyVista plots
        for _, pl in self.pl_list:
            pl.close()

        # close the different Matplotlib plots
        for _, fig in self.fig_list:
            matplotlib.pyplot.close(fig)

    def _get_filename(self, tag, ext):
        """
        Get the plot filenames.
        """

        filename = "%s_%s.%s" % (self.name, tag, ext)
        filename = os.path.join(self.folder, filename)

        return filename

    def _save_screenshot(self):
        """
        Save all the plot content as PNG files.
        """

        # save the PyVista plots
        for tag, pl in self.pl_list:
            filename = self._get_filename(tag, "png")
            pl.screenshot(filename)

        # save the Matplotlib plots
        for tag, fig in self.fig_list:
            filename = self._get_filename(tag, "png")
            fig.savefig(filename)

    def _save_data(self):
        """
        Save all the plot data as VTK files.
        """

        for tag, vtk in self.vtk_list:
            filename = self._get_filename(tag, "vtk")
            vtk.save(filename)

    def open_vtk(self, tag, vtk):
        """
        Add a VTK object.
        """

        self.vtk_list.append((tag, vtk))

    def open_pyvista(self, tag, data_window):
        """
        Get a PyVista plotter.
        """

        # extract the data
        show_menu = data_window["show_menu"]
        image_size = data_window["image_size"]
        window_size = data_window["window_size"]
        notebook_size = data_window["notebook_size"]

        # create the figure
        if self.plot_mode in ["nb_int", "nb_std"]:
            pl = self._get_plotter_pyvista_nb(notebook_size)
        elif self.plot_mode in ["png", "vtk", "debug"]:
            pl = self.__get_plotter_pyvista_base(image_size)
        elif self.plot_mode == "qt":
            pl = self._get_plotter_pyvista_qt(tag, show_menu, window_size)
        else:
            raise ValueError("invalid plot mode")

        # add the plotter to the list
        self.pl_list.append((tag, pl))

        return pl

    def open_matplotlib(self, tag, data_window):
        """
        Get a Matplotlib figure.
        """

        # extract the data
        show_menu = data_window["show_menu"]
        image_size = data_window["image_size"]
        window_size = data_window["window_size"]
        notebook_size = data_window["notebook_size"]

        # create the figure
        if self.plot_mode in ["nb_int", "nb_std"]:
            fig = self._get_figure_matplotlib_nb(notebook_size)
        elif self.plot_mode in ["png", "vtk", "debug"]:
            fig = self._get_figure_matplotlib_base(image_size)
        elif self.plot_mode == "qt":
            fig = self._get_figure_matplotlib_qt(tag, show_menu, window_size)
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
        LOGGER.debug("number of VTK datasets: %s" % len(self.vtk_list))

        if (len(self.pl_list) == 0) and (len(self.fig_list) == 0):
            return

        if self.plot_mode == "nb_int":
            LOGGER.debug("display notebook plots")
            self._show_figure_nb(True)
            LOGGER.debug("exit plotting routine")
        elif self.plot_mode == "nb_std":
            LOGGER.debug("display notebook plots")
            self._show_figure_nb(False)
            LOGGER.debug("exit plotting routine")
        elif self.plot_mode == "png":
            LOGGER.debug("save PNG files")
            self._save_screenshot()
            self._close_figure()
            LOGGER.debug("exit plotting routine")
        elif self.plot_mode == "vtk":
            LOGGER.debug("save VTK files")
            self._save_data()
            self._close_figure()
            LOGGER.debug("exit plotting routine")
        elif self.plot_mode == "debug":
            LOGGER.debug("close all the plots")
            self._close_figure()
            LOGGER.debug("exit plotting routine")
        elif self.plot_mode == "qt":
            LOGGER.debug("entering the plot event loop")
            self._show_figure_qt()
            LOGGER.debug("exiting the plot event loop")
        else:
            raise ValueError("invalid plot mode")
