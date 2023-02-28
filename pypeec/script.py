"""
Contain the console script with CLI interface.
Parse the command line arguments and call the corresponding entry point.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import sys
import argparse
from pypeec import main

# get the version number
try:
    from pypeec import version
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
        allow_abbrev=False,
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
    parser = subparsers.add_parser(
        "mesher",
        aliases=["me"],
        help="transform the provided data into a 3D voxel structure",
    )

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
    parser = subparsers.add_parser(
        "viewer",
        aliases=["vi"],
        help="visualization of a 3D voxel structure",
    )

    # add the arguments
    parser.add_argument(
        "-vo", "--voxel",
        help="voxel file (input / pickle)",
        required=True,
        dest="file_voxel",
    )
    parser.add_argument(
        "-po", "--point",
        help="point file (input / JSON or YAML)",
        required=True,
        dest="file_point",
    )
    parser.add_argument(
        "-vi", "--viewer",
        help="viewer file (input / JSON or YAML)",
        required=True,
        dest="file_viewer",
    )


def _get_arg_solver(subparsers):
    """
    Add the solver arguments.
    """

    # add the subparser
    parser = subparsers.add_parser(
        "solver",
        aliases=["so"],
        help="solve a problem with the PEEC method",
    )

    # add the arguments
    parser.add_argument(
        "-vo", "--voxel",
        help="voxel file (input / pickle)",
        required=True,
        dest="file_voxel",
    )
    parser.add_argument(
        "-pr", "--problem",
        help="problem file (input / JSON or YAML)",
        required=True,
        dest="file_problem",
    )
    parser.add_argument(
        "-to", "--tolerance",
        help="tolerance file (input / JSON or YAML)",
        required=True,
        dest="file_problem",
    )
    parser.add_argument(
        "-so", "--solution",
        help="solution file (output / pickle)",
        required=True,
        dest="file_solution",
    )


def _get_arg_plotter(subparsers):
    """
    Add the plotter arguments.
    """

    # add the subparser
    parser = subparsers.add_parser(
        "plotter",
        aliases=["pl"],
        help="plot the solution of a PEEC problem", 
    )

    # add the arguments
    parser.add_argument(
        "-so", "--solution",
        help="solution file (input / pickle)",
        required=True,
        dest="file_solution",
    )
    parser.add_argument(
        "-po", "--point",
        help="point file (input / JSON or YAML)",
        required=True,
        dest="file_point",
    )
    parser.add_argument(
        "-pl", "--plotter",
        help="plotter file (input / JSON or YAML)",
        required=True,
        dest="file_plotter",
    )


def _get_arguments(parser):
    """
    Parse the command line arguments.
    Load a custom config file (if provided).
    """

    # parse and call
    args = parser.parse_args()

    # get the config file
    command = args.command
    is_interactive = args.is_interactive
    file_config = args.file_config

    # if provided, load a custom config file
    if file_config is not None:
        # load the config
        status = main.set_config(file_config)

        # exit if config is problematic
        if not status:
            sys.exit(1)

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
    if command in ["mesher", "me"]:
        (status, ex) = main.run_mesher(args.file_mesher, args.file_voxel)
    elif command in ["viewer", "vi"]:
        (status, ex) = main.run_viewer(args.file_voxel, args.file_point, args.file_viewer, is_interactive)
    elif command in ["solver", "so"]:
        (status, ex) = main.run_solver(args.file_voxel, args.file_problem, args.file_tolerance, args.file_solution)
    elif command in ["plotter", "pl"]:
        (status, ex) = main.run_plotter(args.file_solution, args.file_point, args.file_plotter, is_interactive)
    else:
        raise ValueError("invalid command")

    # exit the program
    sys.exit(int(not status))


if __name__ == "__main__":
    run_script()