"""
Contain the program entry points.
The import statements for the different modules are located inside the code.
This allows for a minimization of the loaded dependencies.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import os
import sys
import argparse
from PyPEEC.lib_utils import fileio
from PyPEEC.lib_utils import timelogger
from PyPEEC.lib_utils.error import FileError

# get the version
try:
    from PyPEEC import version
    VERSION = version.__version__
except ImportError:
    VERSION = "x.x.x"

# get a logger
logger = timelogger.get_logger("SCRIPT")


def run_mesher(file_mesher, file_voxel):
    """
    Main script for meshing the geometry and generating a 3D voxel structure.
    Write the resulting voxel file.

    Parameters
    ----------
    file_mesher : string (input file, JSON/YAML format)
    file_voxel :  string (output file, Pickle format)

    Returns
    -------
    status : boolean
        True if the call is successful.
        False if the problems are encountered
    """

    logger.info("load the PyPEEC framework")

    from PyPEEC import mesher

    logger.info("init the PyPEEC mesher")

    try:
        # load data
        logger.info("load the input data")
        data_mesher = fileio.load_config(file_mesher)

        # get the path for relative file loading
        path_ref = os.path.dirname(file_mesher)
        path_cwd = os.getcwd()
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
    file_point: string (input file, JSON/YAML format)
    file_viewer: string (input file, JSON/YAML format)
    is_interactive : boolean
        If true, the plots are shown (blocking call).
        If false, the plots are not shown (non-blocking call).

    Returns
    -------
    status : boolean
        True if the call is successful.
        False if the problems are encountered
    """

    logger.info("load the PyPEEC framework")

    from PyPEEC import viewer

    logger.info("init the PyPEEC viewer")

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
    file_problem: string (input file, JSON/YAML format)
    file_tolerance: string (input file, JSON/YAML format)
    file_solution: string (output file, Pickle format)

    Returns
    -------
    status : boolean
        True if the call is successful.
        False if the problems are encountered
    """

    logger.info("load the PyPEEC framework")

    from PyPEEC import solver

    logger.info("init the PyPEEC solver")

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
    file_point: string (input file, JSON/YAML format)
    file_plotter: string (input file, JSON/YAML format)
    is_interactive : boolean
        If true, the plots are shown (blocking call).
        If false, the plots are not shown (non-blocking call).

    Returns
    -------
    status : boolean
        True if the call is successful.
        False if the problems are encountered
    """

    logger.info("load the PyPEEC framework")

    from PyPEEC import plotter

    logger.info("init the PyPEEC plotter")

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


def main_mesher():
    """
    User script for meshing the geometry and generating a 3D voxel structure.
    This script is parsing the command line arguments.
    """

    # get the parser
    parser = argparse.ArgumentParser(
        prog="ppmesher",
        description="PyPEEC mesher: transform the provided data into a 3D voxel structure.",
        epilog="(c) Thomas Guillod - Dartmouth College",
    )
    parser.add_argument('-v', '--version', action='version', version="PyPEEC %s" % VERSION)
    parser.add_argument(
        "--mesher",
        metavar="file",
        help="mesher file (input / JSON/YAML)",
        required=True,
        dest="file_mesher",
    )
    parser.add_argument(
        "--voxel",
        metavar="file",
        help="voxel file (output / pickle)",
        required=True,
        dest="file_voxel",
    )

    # parse and call
    args = parser.parse_args()
    (status, ex) = run_mesher(args.file_mesher, args.file_voxel)
    sys.exit(int(not status))


def main_viewer():
    """
    User script for visualizing a 3D voxel structure.
    This script is parsing the command line arguments.
    """

    # get the parser
    parser = argparse.ArgumentParser(
        prog="ppviewer",
        description="PyPEEC viewer: visualization of a 3D voxel structure.",
        epilog="(c) Thomas Guillod - Dartmouth College",
    )
    parser.add_argument('-v', '--version', action='version', version="PyPEEC %s" % VERSION)
    parser.add_argument(
        "--voxel",
        metavar="file",
        help="voxel file (input / pickle)",
        required=True,
        dest="file_voxel",
    )
    parser.add_argument(
        "--point",
        metavar="file",
        help="point file (input / JSON/YAML)",
        required=True,
        dest="file_point",
    )
    parser.add_argument(
        "--viewer",
        metavar="file",
        help="viewer file (input / JSON/YAML)",
        required=True,
        dest="file_viewer",
    )
    parser.add_argument(
        "--silent",
        help="if set, do not display the plots",
        action="store_false",
        dest="is_interactive",
    )

    # parse and call
    args = parser.parse_args()
    (status, ex) = run_viewer(args.file_voxel, args.file_point, args.file_viewer, args.is_interactive)
    sys.exit(int(not status))


def main_solver():
    """
    User script for solving a problem with the PEEC solver.
    This script is parsing the command line arguments.
    """

    # get the parser
    parser = argparse.ArgumentParser(
        prog="ppsolver",
        description="PyPEEC solver: solve a problem with the PEEC method.",
        epilog="(c) Thomas Guillod - Dartmouth College",
    )
    parser.add_argument('-v', '--version', action='version', version="PyPEEC %s" % VERSION)
    parser.add_argument(
        "--voxel",
        metavar="file",
        help="voxel file (input / pickle)",
        required=True,
        dest="file_voxel",
    )
    parser.add_argument(
        "--problem",
        metavar="file",
        help="problem file (input / JSON/YAML)",
        required=True,
        dest="file_problem",
    )
    parser.add_argument(
        "--tolerance",
        metavar="file",
        help="tolerance file (input / JSON/YAML)",
        required=True,
        dest="file_problem",
    )
    parser.add_argument(
        "--solution",
        metavar="file",
        help="solution file (output / pickle)",
        required=True,
        dest="file_solution",
    )

    # parse and call
    args = parser.parse_args()
    (status, ex) = run_solver(args.file_voxel, args.file_problem, args.file_tolerance, args.file_solution)
    sys.exit(int(not status))


def main_plotter():
    """
    User script for plotting the solution of a PEEC problem.
    This script is parsing the command line arguments.
    """

    # get the parser
    parser = argparse.ArgumentParser(
        prog="ppplotter",
        description="PyPEEC plotter: plot the solution of a PEEC problem.",
        epilog="(c) Thomas Guillod - Dartmouth College",
    )
    parser.add_argument('-v', '--version', action='version', version="PyPEEC %s" % VERSION)
    parser.add_argument(
        "--solution",
        metavar="file",
        help="solution file (input / pickle)",
        required=True,
        dest="file_solution",
    )
    parser.add_argument(
        "--point",
        metavar="file",
        help="point file (input / JSON/YAML)",
        required=True,
        dest="file_point",
    )
    parser.add_argument(
        "--plotter",
        metavar="file",
        help="plotter file (input / JSON/YAML)",
        required=True,
        dest="file_plotter",
    )
    parser.add_argument(
        "--silent",
        help="if set, do not display the plots",
        action="store_false",
        dest="is_interactive",
    )

    # parse and call
    args = parser.parse_args()
    (status, ex) = run_plotter(args.file_solution, args.file_point, args.file_plotter, args.is_interactive)
    sys.exit(int(not status))
