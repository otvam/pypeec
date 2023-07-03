"""
Contain the console script with CLI interface.
Parse the command line arguments and call the corresponding entry point.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

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
        epilog="Thomas Guillod - Dartmouth College",
        allow_abbrev=False,
    )

    # display the version
    parser.add_argument(
        "-v", "--version",
        action="version",
        version="PyPEEC %s" % VERSION,
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
        "-ge", "--geometry",
        help="geometry file (input / JSON or YAML)",
        required=True,
        metavar="file",
        dest="file_geometry",
    )
    parser.add_argument(
        "-vo", "--voxel",
        help="voxel file (output / pickle)",
        required=True,
        metavar="file",
        dest="file_voxel",
    )
    parser.add_argument(
        "-t", "--truncated",
        help="truncate the results (default: full results)",
        action="store_true",
        dest="is_truncated",
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
        metavar="file",
        dest="file_voxel",
    )
    parser.add_argument(
        "-po", "--point",
        help="point file (input / JSON or YAML)",
        required=True,
        metavar="file",
        dest="file_point",
    )
    parser.add_argument(
        "-vi", "--viewer",
        help="viewer file (input / JSON or YAML)",
        required=True,
        metavar="file",
        dest="file_viewer",
    )
    parser.add_argument(
        "-tp", "--tag_plot",
        help="list of plots to be shown (default: show the plots)",
        nargs='+',
        default=None,
        metavar="tag_plot",
        dest="tag_plot",
    )
    parser.add_argument(
        "-pm", "--plot_mode",
        help="selection of the plot mode (default: window)",
        choices=["qt", "nb", "save", "none"],
        default="qt",
        dest="plot_mode",
    )
    parser.add_argument(
        "-f", "--folder",
        help="folder for saving the screenshots (default: cwd)",
        default=None,
        metavar="folder",
        dest="folder",
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
        metavar="file",
        dest="file_voxel",
    )
    parser.add_argument(
        "-pr", "--problem",
        help="problem file (input / JSON or YAML)",
        required=True,
        metavar="file",
        dest="file_problem",
    )
    parser.add_argument(
        "-to", "--tolerance",
        help="tolerance file (input / JSON or YAML)",
        required=True,
        metavar="file",
        dest="file_tolerance",
    )
    parser.add_argument(
        "-so", "--solution",
        help="solution file (output / pickle)",
        required=True,
        metavar="file",
        dest="file_solution",
    )
    parser.add_argument(
        "-t", "--truncated",
        help="truncate the results (default: full results)",
        action="store_true",
        dest="is_truncated",
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
        metavar="file",
        dest="file_solution",
    )
    parser.add_argument(
        "-po", "--point",
        help="point file (input / JSON or YAML)",
        required=True,
        metavar="file",
        dest="file_point",
    )
    parser.add_argument(
        "-pl", "--plotter",
        help="plotter file (input / JSON or YAML)",
        required=True,
        metavar="file",
        dest="file_plotter",
    )
    parser.add_argument(
        "-ts", "--tag_sweep",
        help="list of sweeps to be shown (default: show the sweeps)",
        nargs='+',
        default=None,
        metavar="tag_sweep",
        dest="tag_sweep",
    )
    parser.add_argument(
        "-tp", "--tag_plot",
        help="list of plots to be shown (default: show the plots)",
        nargs='+',
        default=None,
        metavar="tag_plot",
        dest="tag_plot",
    )
    parser.add_argument(
        "-pm", "--plot_mode",
        help="selection of the plot mode (default: window)",
        choices=["qt", "nb", "save", "none"],
        default="qt",
        dest="plot_mode",
    )
    parser.add_argument(
        "-f", "--folder",
        help="folder for saving the screenshots (default: cwd)",
        default=None,
        metavar="folder",
        dest="folder",
    )


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
    args = parser.parse_args()

    # run the code
    if args.command in ["mesher", "me"]:
        (status, ex) = main.run_mesher_file(
            args.file_geometry,
            args.file_voxel,
            is_truncated=args.is_truncated,
        )
    elif args.command in ["viewer", "vi"]:
        (status, ex) = main.run_viewer_file(
            args.file_voxel,
            args.file_point,
            args.file_viewer,
            tag_plot=args.tag_plot,
            plot_mode=args.plot_mode,
            folder=args.folder,
        )
    elif args.command in ["solver", "so"]:
        (status, ex) = main.run_solver_file(
            args.file_voxel,
            args.file_problem,
            args.file_tolerance,
            args.file_solution,
            is_truncated=args.is_truncated,
        )
    elif args.command in ["plotter", "pl"]:
        (status, ex) = main.run_plotter_file(
            args.file_solution,
            args.file_point,
            args.file_plotter,
            tag_sweep=args.tag_sweep,
            tag_plot=args.tag_plot,
            plot_mode=args.plot_mode,
            folder=args.folder,
        )
    else:
        raise ValueError("invalid command")

    # exit the program
    sys.exit(int(not status))


if __name__ == "__main__":
    run_script()
