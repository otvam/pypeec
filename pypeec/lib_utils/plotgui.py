"""
Module for managing plotting windows with PyVista and Matplotlib.
The Qt framework or Jupyter Notebook are used for showing the plots.

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


class PlotGui:
    """
    Manage PyVista and Matplotlib plots.
    Three different plot mode are available:
        - windows: show plot windows with the Qt framework
        - notebook: show the plot inside a Jupyter notebook
        - silent: close all the plots without showing them
    """

    def __init__(self, plot_mode):
        """
        Constructor.
        Init the plots.
        """

        # assign variable
        self.plot_mode = plot_mode
        self.app = None
        self.pl_list = []
        self.fig_list = []

        # setup PyVista and Matplotlib
        if plot_mode == "windows":
            pyvista.set_plot_theme("default")
            matplotlib.use("QtAgg")
        elif plot_mode == "notebook":
            pyvista.set_plot_theme("default")
            pyvista.set_jupyter_backend("trame")
        elif plot_mode == "silent":
            pass
        else:
            raise ValueError("invalid plot mode")

        # create the Qt App
        if plot_mode == "windows":
            self.app = qtpy.QtWidgets.QApplication([])

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
        if self.plot_mode == "windows":
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
        elif self.plot_mode == "notebook":
            # get standard plotter if non-interactive
            pl = pyvista.Plotter(notebook=True, window_size=window_size)
        elif self.plot_mode == "silent":
            # get standard plotter if non-interactive
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
        if self.plot_mode == "windows":
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
        elif self.plot_mode == "notebook":
            fig = matplotlib.pyplot.figure(tight_layout=True)
            fig.set_size_inches(sx/fig.dpi, sy/fig.dpi)
        elif self.plot_mode == "silent":
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
            - windows: show plot windows with the Qt framework (blocking call)
            - notebook: show the plot inside a Jupyter notebook (non-blocking call)
            - silent: close all the plots without showing them (non-blocking call)
        """

        if self.plot_mode == "windows":
            # signal for quitting the event loop with interrupt signal
            signal.signal(signal.SIGINT, signal.SIG_DFL)

            # show the different plots
            for pl in self.pl_list:
                pl.app_window.show()
            matplotlib.pyplot.show(block=False)

            # enter the event loop
            exit_code = self.app.exec_()

            return exit_code == 0
        elif self.plot_mode == "notebook":
            # show the different plots
            for pl in self.pl_list:
                pl.show(jupyter_backend='trame')
            matplotlib.pyplot.show(block=False)

            return True
        elif self.plot_mode == "silent":
            for pl in self.pl_list:
                pl.close()
            for fig in self.fig_list:
                matplotlib.pyplot.close(fig)
        else:
            raise ValueError("invalid plot mode")
