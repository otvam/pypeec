"""
Contain the program entry points.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import sys
import argparse
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


def run_viewer(file_voxel, file_viewer, is_blocking):
    """
    Load the voxel structure and plot the results.
    """

    try:
        # load voxel file
        data_voxel = fileio.load_pickle(file_voxel)

        # load viewer file
        data_viewer = fileio.load_json(file_viewer)

        # call lib_plotter
        status = viewer.run(data_voxel, data_viewer, is_blocking)
    except FileError as ex:
        logger.error("check error : " + str(ex))
        return False

    return status


def run_solver(file_voxel, file_problem, file_solution):
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
        fileio.write_pickle(status, file_solution, data_solution)
    except FileError as ex:
        logger.error("check error : " + str(ex))
        return False

    # exit
    exit_code = int(not status)

    return exit_code


def run_plotter(file_solution, file_plotter, is_blocking):
    """
    Load the solver solution and plot the results.
    """

    try:
        # load res file
        data_solution = fileio.load_pickle(file_solution)

        # load plotter file
        data_plotter = fileio.load_json(file_plotter)

        # call plotter
        status = plotter.run(data_solution, data_plotter, is_blocking)
    except FileError as ex:
        logger.error("check error : " + str(ex))
        return False

    return status


def main_mesher():
    """
    User script for meshing a voxel structure.
    """

    # get the parser
    parser = argparse.ArgumentParser(description="Transform the provided data into a 3D voxel structure.")
    parser.add_argument(
        "--mesher", help="mesher file (input / JSON)",
        required=True, dest="file_mesher"
    )
    parser.add_argument(
        "--voxel", help="voxel file (output / pickle)",
        required=True, dest="file_voxel"
    )

    # parse and call
    args = parser.parse_args()
    status = run_mesher(args.file_mesher, args.file_voxel)
    sys.exit(int(not status))


def main_viewer():
    """
    User script for visualizing a 3D voxel structure..
    """

    # get the parser
    parser = argparse.ArgumentParser(description="Visualization of a 3D voxel structure.")
    parser.add_argument(
        "--voxel", help="voxel file (input / pickle)",
        required=True, dest="file_voxel"
    )
    parser.add_argument(
        "--viewer", help="viewer file (input / JSON)",
        required=True, dest="file_viewer"
    )
    parser.add_argument(
        "--silent", help="if set, do not display the plots",
        action="store_false", dest="is_blocking"
    )

    # parse and call
    args = parser.parse_args()
    status = run_viewer(args.file_voxel, args.file_viewer, args.is_blocking)
    sys.exit(int(not status))


def main_solver():
    """
    User script for solving a problem with the FFT-PEEC solver.
    """

    # get the parser
    parser = argparse.ArgumentParser(description="Solve a problem with the FFT-PEEC method.")
    parser.add_argument(
        "--voxel", help="voxel file (input / pickle)",
        required=True, dest="file_voxel"
    )
    parser.add_argument(
        "--problem", help="problem file (input / JSON)",
        required=True, dest="file_problem"
    )
    parser.add_argument(
        "--solution", help="solution file (output / pickle)",
        required=True, dest="file_solution"
    )

    # parse and call
    args = parser.parse_args()
    status = run_solver(args.file_voxel, args.file_problem, args.file_solution)
    sys.exit(int(not status))


def main_plotter():
    """
    User script for plotting the solution of a FFT-PEEC problem.
    """

    # get the parser
    parser = argparse.ArgumentParser(description="Plot the solution of a FFT-PEEC problem.")
    parser.add_argument(
        "--solution", help="solution file (input / pickle)",
        required=True, dest="file_solution"
    )
    parser.add_argument(
        "--plotter", help="plotter file (input / JSON)",
        required=True, dest="file_plotter"
    )

    # parse and call
    args = parser.parse_args()
    status = run_plotter(args.file_solution, args.file_plotter)
    sys.exit(int(not status))
