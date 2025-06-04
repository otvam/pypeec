"""
Module for managing plotting windows with PyVista and Matplotlib.

Several plot modes are available:
    - The Qt framework is used for rendering the plots.
    - Interactive plots are rendered within the Jupyter notebook.
    - Static plots are rendered within the Jupyter notebook.
    - The plot content are saved as PNG files.
    - The plot data are saved as VTK files.
    - The plots are not shown (debug mode).

The Qt and Jupyter libraries are only imported when used.
This means that this module can run without Qt and Jupyter.

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
import os.path
import ctypes
import signal
import importlib.resources
import matplotlib.pyplot
import matplotlib
import pyvista
import scilogger
import vtk

# get a logger
LOGGER = scilogger.get_logger(__name__, "pypeec")

# prevent VTK to mess up the output
vtk.vtkObject.GlobalWarningDisplayOff()

# variable for the Qt application single instance
APPQT = None


class PlotGui:
    """
    Manage PyVista and Matplotlib plots.
    """

    def __init__(self, plot_mode, path, name):
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

        # set the default for the output path
        if path is None:
            path = os.getcwd()

        # assign variable
        self.plot_mode = plot_mode
        self.path = path
        self.name = name
        self.pl_list = []
        self.fig_list = []
        self.obj_list = []

        # variable for the Qt application single instance
        global APPQT

        # create a single instance of the Qt App
        if (self.plot_mode == "qt") and (APPQT is None):
            # lazy import of the library
            import qtpy.QtWidgets

            # create and assign a single instance
            APPQT = qtpy.QtWidgets.QApplication(["pypeec"])
            APPQT.setApplicationDisplayName("pypeec")
            APPQT.setApplicationName("pypeec")
            APPQT.setOrganizationName("pypeec")

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
    def _set_window_qt(window, title, window_size):
        """
        Set the title, size, and icon of a Qt window.
        """

        # lazy import of the library
        import qtpy.QtGui

        # get the icon
        filename = importlib.resources.files("pypeec.data").joinpath("icon.png")
        res_icon = qtpy.QtGui.QIcon(str(filename))

        # set the Qt options
        window.setWindowTitle(title)
        window.setWindowIcon(res_icon)

        # set window size
        if window_size is not None:
            (sx, sy) = window_size
            window.resize(sx, sy)

    @staticmethod
    def _get_plotter_pyvista_qt(title, show_menu, window_size):
        """
        Create a PyVista plotter for the Qt framework.
        """

        # lazy import of the library
        import pyvistaqt

        # get Qt plotter
        pl = pyvistaqt.BackgroundPlotter(
            show=False,
            toolbar=show_menu,
            menu_bar=show_menu,
        )

        # set the Qt options
        PlotGui._set_window_qt(pl.app_window, title, window_size)

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
    def _get_plotter_pyvista_base(image_size):
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

        # get the figure
        with matplotlib.pyplot.ioff():
            fig = matplotlib.pyplot.figure(tight_layout=True)

        # set the manager
        manager = matplotlib.pyplot.get_current_fig_manager()

        # set the Qt options
        PlotGui._set_window_qt(manager.window, title, window_size)

        # set the menu options
        if show_menu:
            manager.toolbar.show()
        else:
            manager.toolbar.hide()

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

        # return if nothing to be shown
        if (len(self.pl_list) == 0) and (len(self.fig_list) == 0):
            return

        # signal for quitting the event loop with interrupt signal
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        # show the different PyVista plots
        for _, pl in self.pl_list:
            pl.app_window.show()

        # show the different Matplotlib plots
        for _, fig in self.fig_list:
            fig.show()

        # enter the event loop
        status = APPQT.exec()

        # quit app
        APPQT.quit()

        # check status
        if status != 0:
            raise RuntimeError("error during the Qt event loop / exit_code = %d" % status)

    def _show_figure_nb(self, interactive):
        """
        Show all the figures (Jupyter notebooks)
        """

        # return if nothing to be shown
        if (len(self.pl_list) == 0) and (len(self.fig_list) == 0):
            return

        # lazy import of the library
        import IPython.display

        # show the different PyVista plots
        with LOGGER.BlockIndent():
            for tag, pl in self.pl_list:
                LOGGER.debug("show / %s", tag)
                pl.show()

        # show the different Matplotlib plots
        with LOGGER.BlockIndent():
            for tag, fig in self.fig_list:
                LOGGER.debug("show / %s", tag)
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
        filename = os.path.join(self.path, filename)

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

        for tag, obj in self.obj_list:
            filename = self._get_filename(tag, "vtk")
            obj.save(filename)

    def open_vtk(self, tag, obj):
        """
        Add a VTK object.
        """

        self.obj_list.append((tag, obj))

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
            pl = PlotGui._get_plotter_pyvista_nb(notebook_size)
        elif self.plot_mode in ["png", "vtk", "debug"]:
            pl = PlotGui._get_plotter_pyvista_base(image_size)
        elif self.plot_mode == "qt":
            pl = PlotGui._get_plotter_pyvista_qt(tag, show_menu, window_size)
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
            fig = PlotGui._get_figure_matplotlib_nb(notebook_size)
        elif self.plot_mode in ["png", "vtk", "debug"]:
            fig = PlotGui._get_figure_matplotlib_base(image_size)
        elif self.plot_mode == "qt":
            fig = PlotGui._get_figure_matplotlib_qt(tag, show_menu, window_size)
        else:
            raise ValueError("invalid plot mode")

        # add the figure to the list
        self.fig_list.append((tag, fig))

        return fig

    def show(self):
        """
        Finalize the plots (show the plots or save the plots).
        """

        LOGGER.debug("plot statistics")
        with LOGGER.BlockIndent():
            LOGGER.debug("number of 3D plots = %s", len(self.pl_list))
            LOGGER.debug("number of 2D plots = %s", len(self.fig_list))
            LOGGER.debug("number of VTK datasets = %s", len(self.obj_list))

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
