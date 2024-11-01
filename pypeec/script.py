"""
Module containing the command line script.
    - Used for calling the mesher, solver, viewer, and plotter.
    - Parse the command line arguments.
    - Call the corresponding entry point.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import sys
import shutil
import argparse
import importlib.resources
import pypeec


def _run_display_logo():
    """
    Display the logo as a splash screen.
    """

    # load logo data
    with importlib.resources.open_text("pypeec.data", "pypeec.txt") as file:
        data = file.read()

    # display logo
    try:
        data.encode(sys.stderr.encoding)
        print("", flush=True, file=sys.stderr)
        print(data, flush=True, file=sys.stderr)
        print("", flush=True, file=sys.stderr)
    except UnicodeEncodeError:
        pass


def _run_extract(data_name, path_extract):
    """
    Extract data (config, examples, or documentation).

    Parameters
    ----------
    data_name : string
        Name of the file containing the data.
    path_extract : string
        Path where the data will be extracted.
    """

    # init
    print("data extraction: start", flush=True, file=sys.stderr)
    print("data extraction: %s / %s" % (data_name, path_extract), flush=True, file=sys.stderr)

    # execute workflow
    with importlib.resources.path("pypeec.data", data_name) as file:
        shutil.unpack_archive(file, path_extract)

    # teardown
    print("data extraction: finished", flush=True, file=sys.stderr)


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

    # get version
    try:
        with importlib.resources.open_text("pypeec.data", "version.txt") as file:
            version = file.read()
    except FileNotFoundError:
        version = 'x.x.x'

    # display the version
    parser.add_argument(
        "-v", "--version",
        action="version",
        version="PyPEEC %s" % version,
    )

    # hide logo
    parser.add_argument(
        "-q", "--quiet",
        help="do not show the logo  (default: show)",
        action="store_true",
        dest="is_quiet",
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
        help="mesh a geometry into a 3D voxel structure",
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
        "-vi", "--viewer",
        help="viewer file (input / JSON or YAML)",
        required=True,
        metavar="file",
        dest="file_viewer",
    )
    parser.add_argument(
        "-tp", "--tag_plot",
        help="list of plots to be shown (default: all the plots)",
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
        default=".",
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
        help="list of plots to be shown (default: all the plots)",
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
        default=".",
        metavar="folder",
        dest="folder",
    )


def _get_arg_extract(subparsers):
    """
    Add the data extraction arguments (examples and documentation).
    """

    # add the examples data parser
    parser = subparsers.add_parser(
        "examples",
        help="extract the examples",
    )
    parser.add_argument(
        help="path where the examples should be extracted",
        type=str,
        metavar="path",
        dest="path_extract",
    )

    # add the documentation data parser
    parser = subparsers.add_parser(
        "documentation",
        help="extract the documentation",
    )
    parser.add_argument(
        help="path where the documentation should be extracted",
        type=str,
        metavar="path",
        dest="path_extract",
    )


def run_arguments(argv):
    """
    User script for running PyPEEC with given arguments.
        - The script offers a CLI for the mesher, solver, viewer, and plotter.
        - The script can also be used to extract data (examples or documentation).

    Parameters
    ----------
    argv : list
        List with the command line arguments.

    Returns
    -------
    status : int
        The status exit code of the script.

    """

    # get the parser
    (parser, subparsers) = _get_parser()

    # add the sub-command arguments
    _get_arg_mesher(subparsers)
    _get_arg_viewer(subparsers)
    _get_arg_solver(subparsers)
    _get_arg_plotter(subparsers)
    _get_arg_extract(subparsers)

    # parse the config and get arguments
    try:
        args = parser.parse_args(argv)
    except SystemExit as status:
        return status.code

    # display logo
    if not args.is_quiet:
        _run_display_logo()

    # run the code
    try:
        if args.command in ["mesher", "me"]:
            pypeec.run_mesher_file(
                args.file_geometry,
                args.file_voxel,
            )
        elif args.command in ["viewer", "vi"]:
            pypeec.run_viewer_file(
                args.file_voxel,
                args.file_viewer,
                tag_plot=args.tag_plot,
                plot_mode=args.plot_mode,
                folder=args.folder,
            )
        elif args.command in ["solver", "so"]:
            pypeec.run_solver_file(
                args.file_voxel,
                args.file_problem,
                args.file_tolerance,
                args.file_solution,
            )
        elif args.command in ["plotter", "pl"]:
            pypeec.run_plotter_file(
                args.file_solution,
                args.file_plotter,
                tag_sweep=args.tag_sweep,
                tag_plot=args.tag_plot,
                plot_mode=args.plot_mode,
                folder=args.folder,
            )
        elif args.command == "examples":
            _run_extract("examples.zip", args.path_extract)
        elif args.command == "documentation":
            _run_extract("documentation.zip", args.path_extract)
        else:
            raise ValueError("invalid command")
    except Exception:
        return 1
    else:
        return 0


def run_script():
    """
    User script for running PyPEEC with the command line arguments.
        - The script offers a CLI for the mesher, solver, viewer, and plotter.
        - The script can also be used to extract data (examples or documentation).

    The script is installed with the package.
    The name of the command line script is "pypeec".
    Exit the program with "sys.exit()" with a status code.
    """

    # get arguments
    argv = sys.argv[1:]

    # run the script
    status = run_arguments(argv)

    # exit code
    sys.exit(status)
