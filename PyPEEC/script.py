"""
Contain the program entry points.
The import statements for the different modules are located inside the code.
This allows for a minimization of the loaded dependencies.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import os
import sys
import argparse
from PyPEEC.lib_utils import fileio
from PyPEEC.lib_utils import timelogger
from PyPEEC.lib_utils.error import FileError

# get a logger
logger = timelogger.get_logger("SCRIPT")


def run_mesher(file_mesher, file_voxel):
    """
    Main script for meshing the geometry and generating a 3D voxel structure.
    Write the resulting voxel file.

    Parameters
    ----------
    file_mesher : filename (string)
        This file is an input file (JSON format).
        The dict describes the meshing and resampling process.
        The voxel structure can be explicitly given or generated from PNG or STL files.
    file_voxel :  filename (string)
        This file is created during the function call (pickle format).
        The dict describes the voxel structure.
        The voxel grid (number, size, and origin) is defined.
        Different domains (with the indices of the voxel) are defined.
        The connected components of the graph defined by the voxel structure are defined.

    Returns
    -------
    status : boolean
        True if the call is successful.
        False if the problems are encountered
    """

    from PyPEEC import mesher

    try:
        # load data
        logger.info("load the data")
        data_mesher = fileio.load_json(file_mesher)

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
    file_voxel : data (dict)
        This file is an input file (pickle format).
        The dict describes the voxel structure.
        The voxel grid (number, size, and origin) is defined.
        Different domains (with the indices of the voxel) are defined.
        The connected components of the graph defined by the voxel structure are defined.
    file_point: data (array)
        This file is an input file (JSON format).
        The array describes a point cloud.
        The cloud point will be used for field evaluation.
    file_viewer: data (dict)
        This file is an input file (JSON format).
        The list describes the different plots to be created.
        Different types of plots are available.
        Plot of the different domain composing the voxel structure.
        Plot of the connected components composing the voxel structure.
    is_interactive : boolean
        If true, the plots are shown (blocking call).
        If false, the plots are not shown (non-blocking call).

    Returns
    -------
    status : boolean
        True if the call is successful.
        False if the problems are encountered
    """

    from PyPEEC import viewer

    try:
        # load data
        logger.info("load the data")
        data_voxel = fileio.load_pickle(file_voxel)
        data_point = fileio.load_json(file_point)
        data_viewer = fileio.load_json(file_viewer)

        # call the viewer
        (status, ex) = viewer.run(data_voxel, data_point, data_viewer, is_interactive)
    except FileError as ex:
        timelogger.log_exception(logger, ex)
        return False, ex

    return status, ex


def run_solver(file_voxel, file_problem, file_solution):
    """
    Main script for solving a problem with the FFT-PEEC solver.
    Write the resulting solution file.

    Parameters
    ----------
    file_voxel :  filename (string)
        This file is an input file (pickle format).
        The dict describes the voxel structure.
        The voxel grid (number, size, and origin) is defined.
        Different domains (with the indices of the voxel) are defined.
        The connected components of the graph defined by the voxel structure are defined.
    file_problem: filename (string)
        This file is an input file (JSON format).
        The dict describes the problem to be solved.
        The numerical options are defined.
        The frequency of the problem is defined.
        The resistivity of the different domain is defined.
        The current and voltage sources are defined.
    file_solution: filename (string)
        This file is created during the function call (pickle format).
        The dict describes the problem solution.
        The voxel structure is defined.
        The frequency of the problem is defined.
        The status of the solution (solver convergence and condition number) is described.
        The resistivity, potential, and current density of the different voxel is defined.
        The terminals quantities (voltage and current) of the sources are defined.

    Returns
    -------
    status : boolean
        True if the call is successful.
        False if the problems are encountered
    """

    from PyPEEC import solver

    try:
        # load data
        logger.info("load the data")
        data_voxel = fileio.load_pickle(file_voxel)
        data_problem = fileio.load_json(file_problem)

        # call the solver
        (status, data_solution, ex) = solver.run(data_voxel, data_problem)

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
    Main script for plotting the solution of a FFT-PEEC problem.

    Parameters
    ----------
    file_solution :  filename (string)
        This file is an input file (pickle format).
        The dict describes the problem solution.
        The voxel structure is defined.
        The frequency of the problem is defined.
        The status of the solution (solver convergence and condition number) is described.
        The resistivity, potential, and current density of the different voxel is defined.
        The terminals quantities (voltage and current) of the sources are defined.
    file_point: filename (string)
        This file is an input file (JSON format).
        The array describes a point cloud.
        The cloud point is used for field evaluation.
    file_plotter: filename (string)
        This file is an input file (JSON format).
        The list describes the different plots to be created.
        Different types of plots are available.
        Plot showing the conductors and sources.
        Scalar plot of the resistivity of the voxels.
        Scalar plot of the potential and current density of the voxels.
        Vector plot (with arrows) of the current density of the voxels.
        Scalar plot of the magnetic field of the point cloud.
        Vector plot (with arrows) of the magnetic field of the point cloud.
        Plots describing the solver convergence.
    is_interactive : boolean
        If true, the plots are shown (blocking call).
        If false, the plots are not shown (non-blocking call).

    Returns
    -------
    status : boolean
        True if the call is successful.
        False if the problems are encountered
    """

    from PyPEEC import plotter

    try:
        # load data
        logger.info("load the data")
        data_solution = fileio.load_pickle(file_solution)
        data_point = fileio.load_json(file_point)
        data_plotter = fileio.load_json(file_plotter)

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
        description="Transform the provided data into a 3D voxel structure.",
        epilog="(c) Thomas Guillod, Dartmouth College",
    )
    parser.add_argument(
        "--mesher",
        metavar="file",
        help="mesher file (input / JSON)",
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
        description="Visualization of a 3D voxel structure.",
        epilog="(c) Thomas Guillod, Dartmouth College",
    )
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
        help="point file (input / JSON)",
        required=True,
        dest="file_point",
    )
    parser.add_argument(
        "--viewer",
        metavar="file",
        help="viewer file (input / JSON)",
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
    User script for solving a problem with the FFT-PEEC solver.
    This script is parsing the command line arguments.
    """

    # get the parser
    parser = argparse.ArgumentParser(
        prog="ppsolver",
        description="Solve a problem with the FFT-PEEC method.",
        epilog="(c) Thomas Guillod, Dartmouth College",
    )
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
        help="problem file (input / JSON)",
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
    (status, ex) = run_solver(args.file_voxel, args.file_problem, args.file_solution)
    sys.exit(int(not status))


def main_plotter():
    """
    User script for plotting the solution of a FFT-PEEC problem.
    This script is parsing the command line arguments.
    """

    # get the parser
    parser = argparse.ArgumentParser(
        prog="ppplotter",
        description="Plot the solution of a FFT-PEEC problem.",
        epilog="(c) Thomas Guillod, Dartmouth College",
    )
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
        help="point file (input / JSON)",
        required=True,
        dest="file_point",
    )
    parser.add_argument(
        "--plotter",
        metavar="file",
        help="plotter file (input / JSON)",
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
