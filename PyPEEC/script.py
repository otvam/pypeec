"""
Contain the console scripts (mesher, viewer, solver, and plotter).
Parse the command line arguments and call the corresponding entry point.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import sys
import argparse
from PyPEEC import main

# get the version
try:
    from PyPEEC import version
    VERSION = version.__version__
except ImportError:
    VERSION = "x.x.x"


def run_mesher():
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
    parser.add_argument("-v", "--version", action="version", version="PyPEEC %s" % VERSION)
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
    (status, ex) = main.run_mesher(args.file_mesher, args.file_voxel)
    sys.exit(int(not status))


def run_viewer():
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
    parser.add_argument("-v", "--version", action="version", version="PyPEEC %s" % VERSION)
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
    (status, ex) = main.run_viewer(args.file_voxel, args.file_point, args.file_viewer, args.is_interactive)
    sys.exit(int(not status))


def run_solver():
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
    parser.add_argument("-v", "--version", action="version", version="PyPEEC %s" % VERSION)
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
    (status, ex) = main.run_solver(args.file_voxel, args.file_problem, args.file_tolerance, args.file_solution)
    sys.exit(int(not status))


def run_plotter():
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
    parser.add_argument("-v", "--version", action="version", version="PyPEEC %s" % VERSION)
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
    (status, ex) = main.run_plotter(args.file_solution, args.file_point, args.file_plotter, args.is_interactive)
    sys.exit(int(not status))
