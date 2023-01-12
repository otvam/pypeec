"""
Contain the program entry points.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

from PyPEEC import mesher
from PyPEEC import viewer
from PyPEEC import solver
from PyPEEC import plotter
from PyPEEC.lib_utils import fileio
from PyPEEC.lib_utils import timelogger
from PyPEEC.lib_utils.error import FileError

# get a logger
logger = timelogger.get_logger("script")


def run_mesher(file_mesher, file_voxel):
    """
    Solve the problem and write the mesher results.
    """

    try:
        # load mesher file
        data_mesher = fileio.load_json(file_mesher)

        # call solver
        (status, data_voxel) = mesher.run(data_mesher)

        # save results
        fileio.write_pickle(status, file_voxel, data_voxel)
    except FileError as ex:
        logger.error("check error : " + str(ex))
        return False

    return status


def run_viewer(file_voxel, file_viewer):
    """
    Load the voxel structure and plot the results.
    """

    try:
        # load voxel file
        data_voxel = fileio.load_pickle(file_voxel)

        # load viewer file
        data_viewer = fileio.load_json(file_viewer)

        # call lib_plotter
        status = viewer.run(data_voxel, data_viewer)
    except FileError as ex:
        logger.error("check error : " + str(ex))
        return False

    return status


def run_solver(file_voxel, file_problem, file_res):
    """
    Load the voxel structure, solve the problem and write the solver results.
    """

    try:
        # load voxel file
        data_voxel = fileio.load_pickle(file_voxel)

        # load mesher file
        data_problem = fileio.load_json(file_problem)

        # call solver
        (status, data_solution) = solver.run(data_voxel, data_problem)

        # save results
        fileio.write_pickle(status, file_res, data_solution)
    except FileError as ex:
        logger.error("check error : " + str(ex))
        return False

    # exit
    exit_code = int(not status)

    return exit_code


def run_plotter(file_res, file_plotter):
    """
    Load the solver solution and plot the results.
    """

    try:
        # load res file
        data_solution = fileio.load_pickle(file_res)

        # load plotter file
        data_plotter = fileio.load_json(file_plotter)

        # call plotter
        status = plotter.run(data_solution, data_plotter)
    except FileError as ex:
        logger.error("check error : " + str(ex))
        return False

    return status
