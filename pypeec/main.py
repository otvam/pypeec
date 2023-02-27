"""
Contain the program entry points (mesher, viewer, solver, and plotter).
The import statements for the different modules are located inside the code.
This allows for a minimization of the loaded dependencies.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import os
import os.path
from pypeec.lib_utils import timelogger
from pypeec.lib_utils import config
from pypeec.lib_utils import fileio
from pypeec.lib_utils.error import FileError, CheckError

# get a logger
logger = timelogger.get_logger("MAIN")


def set_config(file_config):
    """
    Set and load a custom configuration file.
    This function should be called immediately after initializing the module.

    Parameters
    ----------
    file_config : string (input file, JSON or YAML format)

    Returns
    -------
    status : boolean
        True if the call is successful.
        False if the problems are encountered
    """

    logger.info("set the PyPEEC configuration")

    try:
        config.set_config(file_config)
    except (FileError, CheckError) as ex:
        timelogger.log_exception(logger, ex)
        return False

    return True


def run_mesher(file_mesher, file_voxel):
    """
    Main script for meshing the geometry and generating a 3D voxel structure.
    Write the resulting voxel file.

    Parameters
    ----------
    file_mesher : string (input file, JSON or YAML format)
    file_voxel :  string (output file, Pickle format)

    Returns
    -------
    status : boolean
        True if the call is successful.
        False if the problems are encountered
    """

    # load the tool
    logger.info("load the mesher")
    from pypeec import mesher

    # run the tool
    try:
        # load data
        logger.info("load the input data")
        data_mesher = fileio.load_config(file_mesher)

        # get the path for relative file loading
        path_cwd = os.getcwd()
        path_ref = os.path.dirname(file_mesher)
        path_ref = os.path.relpath(path_ref, path_cwd)

        # call the mesher
        (status, data_voxel, ex) = mesher.run(data_mesher, path_ref)

        # save results
        if status:
            logger.info("save the results")
            fileio.write_pickle(file_voxel, data_voxel)
    except FileError as ex:
        timelogger.log_exception(logger, ex)
        return False, ex

    return status, ex


def run_viewer(file_voxel, file_point, file_viewer, is_interactive):
    """
    Main script for visualizing a 3D voxel structure.

    Parameters
    ----------
    file_voxel : string (input file, Pickle format)
    file_point: string (input file, JSON or YAML format)
    file_viewer: string (input file, JSON or YAML format)
    is_interactive : boolean
        If true, the plots are shown (blocking call).
        If false, the plots are not shown (non-blocking call).

    Returns
    -------
    status : boolean
        True if the call is successful.
        False if the problems are encountered
    """

    # load the tool
    logger.info("load the viewer")
    from pypeec import viewer

    # run the tool
    try:
        # load data
        logger.info("load the input data")
        data_voxel = fileio.load_pickle(file_voxel)
        data_point = fileio.load_config(file_point)
        data_viewer = fileio.load_config(file_viewer)

        # call the viewer
        (status, ex) = viewer.run(data_voxel, data_point, data_viewer, is_interactive)
    except FileError as ex:
        timelogger.log_exception(logger, ex)
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
        False if the problems are encountered
    """

    # load the tool
    logger.info("load the solver")
    from pypeec import solver

    # run the tool
    try:
        # load data
        logger.info("load the input data")
        data_voxel = fileio.load_pickle(file_voxel)
        data_problem = fileio.load_config(file_problem)
        data_tolerance = fileio.load_config(file_tolerance)

        # call the solver
        (status, data_solution, ex) = solver.run(data_voxel, data_problem, data_tolerance)

        # save results
        if status:
            logger.info("save the results")
            fileio.write_pickle(file_solution, data_solution)
    except FileError as ex:
        timelogger.log_exception(logger, ex)
        return False, ex

    return status, ex


def run_plotter(file_solution, file_point, file_plotter, is_interactive):
    """
    Main script for plotting the solution of a PEEC problem.

    Parameters
    ----------
    file_solution : string (input file, Pickle format)
    file_point: string (input file, JSON or YAML format)
    file_plotter: string (input file, JSON or YAML format)
    is_interactive : boolean
        If true, the plots are shown (blocking call).
        If false, the plots are not shown (non-blocking call).

    Returns
    -------
    status : boolean
        True if the call is successful.
        False if the problems are encountered
    """

    # load the tool
    logger.info("load the plotter")
    from pypeec import plotter

    # run the tool
    try:
        # load data
        logger.info("load the input data")
        data_solution = fileio.load_pickle(file_solution)
        data_point = fileio.load_config(file_point)
        data_plotter = fileio.load_config(file_plotter)

        # call the plotter
        (status, ex) = plotter.run(data_solution, data_point, data_plotter, is_interactive)
    except FileError as ex:
        timelogger.log_exception(logger, ex)
        return False, ex

    return status, ex
