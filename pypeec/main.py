"""
Contain the program entry points (mesher, viewer, solver, and plotter).
The import statements for the different modules are located inside the code.
This allows for a minimization of the loaded dependencies.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import os.path
from pypeec import utils_log
from pypeec import utils_io
from pypeec.error import FileError


def run_mesher(file_geometry, file_voxel):
    """
    Main script for meshing the geometry and generating a 3D voxel structure.
    Write the resulting voxel file.

    Parameters
    ----------
    file_geometry : string (input file, JSON or YAML format)
    file_voxel :  string (output file, Pickle format)

    Returns
    -------
    status : boolean
        True if the call is successful.
        False if the problems are encountered.
    ex : exception
        The encountered exception (if any).
        None if the termination is successful.
    """

    # create the logger
    logger = utils_log.get_logger("MAIN")

    # reset the timer logger

    # load the tool
    logger.info("load the mesher")
    from pypeec import mesher

    # run the tool
    try:
        # load data
        logger.info("load the input data")
        data_geometry = utils_io.load_config(file_geometry)

        # get the path for relative file loading
        pathref = os.path.abspath(file_geometry)
        pathref = os.path.dirname(pathref)

        # call the mesher
        (status, data_voxel, ex) = mesher.run(data_geometry, pathref)

        # save results
        if status:
            logger.info("save the results")
            utils_io.write_pickle(file_voxel, data_voxel)
    except FileError as ex:
        utils_log.log_exception(logger, ex)
        return False, ex

    return status, ex


def run_viewer(file_voxel, file_point, file_viewer, tag_plot=None, is_silent=False):
    """
    Main script for visualizing a 3D voxel structure.

    Parameters
    ----------
    file_voxel : string (input file, Pickle format)
    file_point: string (input file, JSON or YAML format)
    file_viewer: string (input file, JSON or YAML format)
    tag_plot : list
        The list describes plots to be shown.
        If None, all the plots are shown.
    is_silent : boolean
        If true, the plots are not shown (non-blocking call).
        If true, the plots are shown (blocking call).

    Returns
    -------
    status : boolean
        True if the call is successful.
        False if the problems are encountered.
    ex : exception
        The encountered exception (if any).
        None if the termination is successful.
    """

    # create the logger
    logger = utils_log.get_logger("MAIN")

    # load the tool
    logger.info("load the viewer")
    from pypeec import viewer

    # run the tool
    try:
        # load data
        logger.info("load the input data")
        data_voxel = utils_io.load_pickle(file_voxel)
        data_point = utils_io.load_config(file_point)
        data_viewer = utils_io.load_config(file_viewer)

        # call the viewer
        (status, ex) = viewer.run(data_voxel, data_point, data_viewer, tag_plot, is_silent)
    except FileError as ex:
        utils_log.log_exception(logger, ex)
        return False, ex

    return status, ex


def run_solver(file_voxel, file_problem, file_tolerance, file_solution):
    """
    Main script for solving a problem with the PEEC solver.
    Write the resulting solution file.

    Parameters
    ----------
    file_voxel :  string (input file, Pickle format)
    file_problem: string (input file, JSON or YAML format)
    file_tolerance: string (input file, JSON or YAML format)
    file_solution: string (output file, Pickle format)

    Returns
    -------
    status : boolean
        True if the call is successful.
        False if the problems are encountered.
    ex : exception
        The encountered exception (if any).
        None if the termination is successful.
    """

    # create the logger
    logger = utils_log.get_logger("MAIN")

    # load the tool
    logger.info("load the solver")
    from pypeec import solver

    # run the tool
    try:
        # load data
        logger.info("load the input data")
        data_voxel = utils_io.load_pickle(file_voxel)
        data_problem = utils_io.load_config(file_problem)
        data_tolerance = utils_io.load_config(file_tolerance)

        # call the solver
        (status, data_solution, ex) = solver.run(data_voxel, data_problem, data_tolerance)

        # save results
        if status:
            logger.info("save the results")
            utils_io.write_pickle(file_solution, data_solution)
    except FileError as ex:
        utils_log.log_exception(logger, ex)
        return False, ex

    return status, ex


def run_plotter(file_solution, file_point, file_plotter, tag_sweep=None, tag_plot=None, is_silent=False):
    """
    Main script for plotting the solution of a PEEC problem.

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
    is_silent : boolean
        If true, the plots are not shown (non-blocking call).
        If true, the plots are shown (blocking call).

    Returns
    -------
    status : boolean
        True if the call is successful.
        False if the problems are encountered.
    ex : exception
        The encountered exception (if any).
        None if the termination is successful.
    """

    # create the logger
    logger = utils_log.get_logger("MAIN")

    # load the tool
    logger.info("load the plotter")
    from pypeec import plotter

    # run the tool
    try:
        # load data
        logger.info("load the input data")
        data_solution = utils_io.load_pickle(file_solution)
        data_point = utils_io.load_config(file_point)
        data_plotter = utils_io.load_config(file_plotter)

        # call the plotter
        (status, ex) = plotter.run(data_solution, data_point, data_plotter, tag_sweep, tag_plot, is_silent)
    except FileError as ex:
        utils_log.log_exception(logger, ex)
        return False, ex

    return status, ex
