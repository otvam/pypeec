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


def _get_parser():
    """
    Create a command line parser with a description.
    """

    # get the parser
    parser = argparse.ArgumentParser(
        prog="pypeec",
        description="PyPEEC - 3D PEEC Solver",
        epilog="(c) Thomas Guillod - Dartmouth College",
    )

    # display the version
    parser.add_argument(
        "-v", "--version",
        action="version",
        version="PyPEEC %s" % VERSION,
    )

    # silent mode
    parser.add_argument(
        "-s", "--silent",
        help="if set, do not display the plots",
        action="store_false",
        dest="is_interactive",
    )

    # switch for a custom config file
    parser.add_argument(
        "-c", "--config",
        help="config file (custom configuration file / JSON or YAML)",
        required=False,
        dest="file_config",
    )

    # add subparsers
    subparsers = parser.add_subparsers(
        required=True,
        dest="command",
        title="command",
    )

    return parser, subparsers


def _get_arg_mesher(subparsers):
    """
    Add the mesher arguments.
    """

    # add the subparser
    parser = subparsers.add_parser('mesher', help="transform the provided data into a 3D voxel structure")

    # add the arguments
    parser.add_argument(
        "-me", "--mesher",
        help="mesher file (input / JSON or YAML)",
        required=True,
        dest="file_mesher",
    )
    parser.add_argument(
        "-vo", "--voxel",
        help="voxel file (output / pickle)",
        required=True,
        dest="file_voxel",
    )


def _get_arg_viewer(subparsers):
    """
    Add the viewer arguments.
    """

    # add the subparser
    parser = subparsers.add_parser('viewer', help="visualization of a 3D voxel structure")

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


def _get_arg_solver(subparsers):
    """
    Add the solver arguments.
    """

    # add the subparser
    parser = subparsers.add_parser('solver', help="solve a problem with the PEEC method")

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


def _get_arg_plotter(subparsers):
    """
    Add the plotter arguments.
    """

    # add the subparser
    parser = subparsers.add_parser('plotter', help="plot the solution of a PEEC problem")

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


def _get_arguments(parser):
    """
    Load the config file (if specified).
    """

    # parse and call
    args = parser.parse_args()

    # get the config file
    command = args.command
    is_interactive = args.is_interactive
    file_config = args.file_config

    # load the config
    if file_config is not None:
        status = main.set_config(file_config)
    else:
        status = True

    # exit if problematic
    if not status:
        sys.exit(int(not status))

    return command, is_interactive, args


def run_script():
    """
    User script for running PyPEEC.
    This script is parsing the command line arguments.
    """

    # get the parser
    (parser, subparsers) = _get_parser()

    # add the sub-command arguments
    _get_arg_mesher(subparsers)
    _get_arg_viewer(subparsers)
    _get_arg_solver(subparsers)
    _get_arg_plotter(subparsers)

    # parse the config and get arguments
    (command, is_interactive, args) = _get_arguments(parser)

    # run the code
    if command == "mesher":
        (status, ex) = main.run_mesher(args.file_mesher, args.file_voxel)
    elif command == "viewer":
        (status, ex) = main.run_viewer(args.file_voxel, args.file_point, args.file_viewer, is_interactive)
    elif command == "solver":
        (status, ex) = main.run_solver(args.file_voxel, args.file_problem, args.file_tolerance, args.file_solution)
    elif command == "plotter":
        (status, ex) = main.run_plotter(args.file_solution, args.file_point, args.file_plotter, is_interactive)
    else:
        raise ValueError("invalid command")

    # exit the program
    sys.exit(int(not status))


if __name__ == "__main__":
    run_script()
