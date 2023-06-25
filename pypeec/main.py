"""
Contain the program entry points (mesher, viewer, solver, and plotter).
The import statements for the different modules are located inside the code.
This allows for a minimization of the loaded dependencies.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

from pypeec import log
from pypeec import io
from pypeec.error import FileError

# create the logger
LOGGER = log.get_logger("MAIN")


def run_mesher_data(data_geometry, is_truncated=False):
    """
    Main script for meshing the geometry and generating a 3D voxel structure.

    Parameters
    ----------
    data_geometry : dict (input data)
    is_truncated : boolean
        If true, the results are truncated to save space.
        If false, the complete results are returned.

    Returns
    -------
    status : boolean
        True if the call is successful.
        False if problems are encountered.
    ex : exception
        The encountered exception (if any).
        None if the termination is successful.
    data_voxel: dict (output data)
    """

    # load the tool
    from pypeec.run import mesher

    # run the tool
    (status, ex, data_voxel) = mesher.run(data_geometry, is_truncated)

    return status, ex, data_voxel


def run_mesher_file(file_geometry, file_voxel, is_truncated=False):
    """
    Main script for meshing the geometry and generating a 3D voxel structure.
    Load the input data from files.
    Write the resulting voxel file.

    Parameters
    ----------
    file_geometry : string (input file, JSON or YAML format)
    file_voxel :  string (output file, Pickle format)
    is_truncated : boolean
        If true, the results are truncated to save space.
        If false, the complete results are returned.

    Returns
    -------
    status : boolean
        True if the call is successful.
        False if problems are encountered.
    ex : exception
        The encountered exception (if any).
        None if the termination is successful.
    """

    # load the tool
    LOGGER.info("load the mesher")
    from pypeec.run import mesher

    # run the tool
    try:
        # load data
        LOGGER.info("load the input data")
        data_geometry = io.load_config(file_geometry)

        # call the mesher
        (status, ex, data_voxel) = mesher.run(data_geometry, is_truncated)

        # save results
        LOGGER.info("save the results")
        io.write_pickle(file_voxel, data_voxel)
    except FileError as ex:
        log.log_exception(LOGGER, ex)
        return False, ex

    return status, ex


def run_viewer_data(
        data_voxel, data_point, data_viewer,
        tag_plot=None, plot_mode="qt", folder=".",
):
    """
    Main script for visualizing a 3D voxel structure.

    Parameters
    ----------
    data_voxel : dict (input data)
    data_point: list (input data)
    data_viewer: dict (input data)
    tag_plot : list
        The list describes plots to be shown.
        If None, all the plots are shown.
    plot_mode : string
        If "qt", the Qt framework is used for the rendering (default).
        If "nb", the plots are rendered within the Jupyter notebook.
        If "save", the plots are not shown but saved as screenshots.
        If "none", the plots are not shown (test mode).
    folder : string
        Folder name for saving the screenshots.
        The current directory is used as the default directory.

    Returns
    -------
    status : boolean
        True if the call is successful.
        False if problems are encountered.
    ex : exception
        The encountered exception (if any).
        None if the termination is successful.
    """

    # load the tool
    from pypeec.run import viewer

    # run the tool
    (status, ex) = viewer.run(data_voxel, data_point, data_viewer, tag_plot, plot_mode, folder)

    return status, ex


def run_viewer_file(
        file_voxel, file_point, file_viewer,
        tag_plot=None, plot_mode="qt", folder=".",
):
    """
    Main script for visualizing a 3D voxel structure.
    Load the input data from files.

    Parameters
    ----------
    file_voxel : string (input file, Pickle format)
    file_point: string (input file, JSON or YAML format)
    file_viewer: string (input file, JSON or YAML format)
    tag_plot : list
        The list describes plots to be shown.
        If None, all the plots are shown.
    plot_mode : string
        If "qt", the Qt framework is used for the rendering (default).
        If "nb", the plots are rendered within the Jupyter notebook.
        If "save", the plots are not shown but saved as screenshots.
        If "none", the plots are not shown (test mode).
    folder : string
        Folder name for saving the screenshots.
        The current directory is used as the default directory.

    Returns
    -------
    status : boolean
        True if the call is successful.
        False if problems are encountered.
    ex : exception
        The encountered exception (if any).
        None if the termination is successful.
    """

    # load the tool
    LOGGER.info("load the viewer")
    from pypeec.run import viewer

    # run the tool
    try:
        # load data
        LOGGER.info("load the input data")
        data_voxel = io.load_pickle(file_voxel)
        data_point = io.load_config(file_point)
        data_viewer = io.load_config(file_viewer)

        # call the viewer
        (status, ex) = viewer.run(data_voxel, data_point, data_viewer, tag_plot, plot_mode, folder)
    except FileError as ex:
        log.log_exception(LOGGER, ex)
        return False, ex

    return status, ex


def run_solver_data(data_voxel, data_problem, data_tolerance, is_truncated=False):
    """
    Main script for solving a problem with the PEEC solver.

    Parameters
    ----------
    data_voxel :  dict (input data)
    data_problem: dict (input data)
    data_tolerance: dict (input data)
    is_truncated : boolean
        If true, the results are truncated to save space.
        If false, the complete results are returned.

    Returns
    -------
    status : boolean
        True if the call is successful.
        False if problems are encountered.
    ex : exception
        The encountered exception (if any).
        None if the termination is successful.
    data_solution: dict (output data)
    """

    # load the tool
    from pypeec.run import solver

    # run the tool
    (status, ex, data_solution) = solver.run(data_voxel, data_problem, data_tolerance, is_truncated)

    return status, ex, data_solution


def run_solver_file(file_voxel, file_problem, file_tolerance, file_solution, is_truncated=False):
    """
    Main script for solving a problem with the PEEC solver.
    Load the input data from files.
    Write the resulting solution file.

    Parameters
    ----------
    file_voxel :  string (input file, Pickle format)
    file_problem: string (input file, JSON or YAML format)
    file_tolerance: string (input file, JSON or YAML format)
    file_solution: string (output file, Pickle format)
    is_truncated : boolean
        If true, the results are truncated to save space.
        If false, the complete results are returned.

    Returns
    -------
    status : boolean
        True if the call is successful.
        False if problems are encountered.
    ex : exception
        The encountered exception (if any).
        None if the termination is successful.
    """

    # load the tool
    LOGGER.info("load the solver")
    from pypeec.run import solver

    # run the tool
    try:
        # load data
        LOGGER.info("load the input data")
        data_voxel = io.load_pickle(file_voxel)
        data_problem = io.load_config(file_problem)
        data_tolerance = io.load_config(file_tolerance)

        # call the solver
        (status, ex, data_solution) = solver.run(data_voxel, data_problem, data_tolerance, is_truncated)

        # save results
        LOGGER.info("save the results")
        io.write_pickle(file_solution, data_solution)
    except FileError as ex:
        log.log_exception(LOGGER, ex)
        return False, ex

    return status, ex


def run_plotter_data(
        data_solution, data_point, data_plotter,
        tag_sweep=None, tag_plot=None, plot_mode="qt", folder=".",
):
    """
    Main script for plotting the solution of a PEEC problem.

    Parameters
    ----------
    data_solution : dict (input data)
    data_point: list (input data)
    data_plotter: dict (input data)
    tag_sweep : list
        The list describes sweeps to be shown.
        If None, all the sweeps are shown.
    tag_plot : list
        The list describes plots to be shown.
        If None, all the plots are shown.
    plot_mode : string
        If "qt", the Qt framework is used for the rendering (default).
        If "nb", the plots are rendered within the Jupyter notebook.
        If "save", the plots are not shown but saved as screenshots.
        If "none", the plots are not shown (test mode).
    folder : string
        Folder name for saving the screenshots.
        The current directory is used as the default directory.

    Returns
    -------
    status : boolean
        True if the call is successful.
        False if problems are encountered.
    ex : exception
        The encountered exception (if any).
        None if the termination is successful.
    """

    # load the tool
    from pypeec.run import plotter

    # run the tool
    (status, ex) = plotter.run(data_solution, data_point, data_plotter, tag_sweep, tag_plot, plot_mode, folder)

    return status, ex


def run_plotter_file(
        file_solution, file_point, file_plotter,
        tag_sweep=None, tag_plot=None, plot_mode="qt", folder=".",
):
    """
    Main script for plotting the solution of a PEEC problem.
    Load the input data from files.

    Parameters
    ----------
    file_solution : string (input file, Pickle format)
    file_point: string (input file, JSON or YAML format)
    file_plotter: string (input file, JSON or YAML format)
    tag_sweep : list
        The list describes sweeps to be shown.
        If None, all the sweeps are shown.
    tag_plot : list
        The list describes plots to be shown.
        If None, all the plots are shown.
    plot_mode : string
        If "qt", the Qt framework is used for the rendering (default).
        If "nb", the plots are rendered within the Jupyter notebook.
        If "save", the plots are not shown but saved as screenshots.
        If "none", the plots are not shown (test mode).
    folder : string
        Folder name for saving the screenshots.
        The current directory is used as the default directory.

    Returns
    -------
    status : boolean
        True if the call is successful.
        False if problems are encountered.
    ex : exception
        The encountered exception (if any).
        None if the termination is successful.
    """

    # load the tool
    LOGGER.info("load the plotter")
    from pypeec.run import plotter

    # run the tool
    try:
        # load data
        LOGGER.info("load the input data")
        data_solution = io.load_pickle(file_solution)
        data_point = io.load_config(file_point)
        data_plotter = io.load_config(file_plotter)

        # call the plotter
        (status, ex) = plotter.run(data_solution, data_point, data_plotter, tag_sweep, tag_plot, plot_mode, folder)
    except FileError as ex:
        log.log_exception(LOGGER, ex)
        return False, ex

    return status, ex
