"""
Contain the console scripts (mesher, viewer, solver, and plotter).
Parse the command line arguments and call the corresponding entry point.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import sys
import argparse
from PyPEEC import main

# get the version number
try:
    from PyPEEC import version
    VERSION = version.__version__
except ImportError:
    VERSION = "x.x.x"


def _get_parser(prog, description):
    """
    Create a command line parser with a description.
    """

    # get the parser
    parser = argparse.ArgumentParser(
        prog=prog,
        description=description,
        epilog="(c) Thomas Guillod - Dartmouth College",
    )

    # display the version
    parser.add_argument(
        "-v", "--version",
        action="version",
        version="PyPEEC %s" % VERSION,
    )

    # switch for a custom config file
    parser.add_argument(
        "-c", "--config",
        metavar="file",
        help="config file (input / JSON or YAML)",
        required=False,
        dest="file_config",
    )

    return parser


def _get_arguments(parser):
    """
    Load the config file (if specified).
    """

    # parse and call
    args = parser.parse_args()

    # get the config file
    file_config = args.file_config

    # load the config
    if file_config is not None:
        status = main.set_config(file_config)
    else:
        status = True

    # exit if problematic
    if not status:
        sys.exit(int(not status))

    return args


def run_mesher():
    """
    User script for meshing the geometry and generating a 3D voxel structure.
    This script is parsing the command line arguments.
    """

    # get the parser
    parser = _get_parser("ppmesher", "PyPEEC mesher: transform the provided data into a 3D voxel structure")

    # add the arguments
    parser.add_argument(
        "-me", "--mesher",
        metavar="file",
        help="mesher file (input / JSON or YAML)",
        required=True,
        dest="file_mesher",
    )
    parser.add_argument(
        "-vo", "--voxel",
        metavar="file",
        help="voxel file (output / pickle)",
        required=True,
        dest="file_voxel",
    )

    # parse the config and get arguments
    args = _get_arguments(parser)

    # run the code
    (status, ex) = main.run_mesher(args.file_mesher, args.file_voxel)
    sys.exit(int(not status))


def run_viewer():
    """
    User script for visualizing a 3D voxel structure.
    This script is parsing the command line arguments.
    """

    # get the parser
    parser = _get_parser("ppviewer", "PyPEEC viewer: visualization of a 3D voxel structure")

    # add the arguments
    parser.add_argument(
        "-vo", "--voxel",
        metavar="file",
        help="voxel file (input / pickle)",
        required=True,
        dest="file_voxel",
    )
    parser.add_argument(
        "-po", "--point",
        metavar="file",
        help="point file (input / JSON or YAML)",
        required=True,
        dest="file_point",
    )
    parser.add_argument(
        "-vi", "--viewer",
        metavar="file",
        help="viewer file (input / JSON or YAML)",
        required=True,
        dest="file_viewer",
    )
    parser.add_argument(
        "-s", "--silent",
        help="if set, do not display the plots",
        action="store_false",
        dest="is_interactive",
    )

    # parse the config and get arguments
    args = _get_arguments(parser)

    # run the code
    (status, ex) = main.run_viewer(args.file_voxel, args.file_point, args.file_viewer, args.is_interactive)
    sys.exit(int(not status))


def run_solver():
    """
    User script for solving a problem with the PEEC solver.
    This script is parsing the command line arguments.
    """

    # get the parser
    parser = _get_parser("ppsolver", "PyPEEC solver: solve a problem with the PEEC method")

    # add the arguments
    parser.add_argument(
        "-vo", "--voxel",
        metavar="file",
        help="voxel file (input / pickle)",
        required=True,
        dest="file_voxel",
    )
    parser.add_argument(
        "-pr", "--problem",
        metavar="file",
        help="problem file (input / JSON or YAML)",
        required=True,
        dest="file_problem",
    )
    parser.add_argument(
        "-to", "--tolerance",
        metavar="file",
        help="tolerance file (input / JSON or YAML)",
        required=True,
        dest="file_problem",
    )
    parser.add_argument(
        "-so", "--solution",
        metavar="file",
        help="solution file (output / pickle)",
        required=True,
        dest="file_solution",
    )

    # parse the config and get arguments
    args = _get_arguments(parser)

    # run the code
    (status, ex) = main.run_solver(args.file_voxel, args.file_problem, args.file_tolerance, args.file_solution)
    sys.exit(int(not status))


def run_plotter():
    """
    User script for plotting the solution of a PEEC problem.
    This script is parsing the command line arguments.
    """

    # get the parser
    parser = _get_parser("ppplotter", "PyPEEC plotter: plot the solution of a PEEC problem")

    # add the arguments
    parser.add_argument(
        "-so", "--solution",
        metavar="file",
        help="solution file (input / pickle)",
        required=True,
        dest="file_solution",
    )
    parser.add_argument(
        "-po", "--point",
        metavar="file",
        help="point file (input / JSON or YAML)",
        required=True,
        dest="file_point",
    )
    parser.add_argument(
        "-pl", "--plotter",
        metavar="file",
        help="plotter file (input / JSON or YAML)",
        required=True,
        dest="file_plotter",
    )
    parser.add_argument(
        "-s", "--silent",
        help="if set, do not display the plots",
        action="store_false",
        dest="is_interactive",
    )

    # parse the config and get arguments
    args = _get_arguments(parser)

    # run the code
    (status, ex) = main.run_plotter(args.file_solution, args.file_point, args.file_plotter, args.is_interactive)
    sys.exit(int(not status))
