"""
Module for running the PyPEEC workflow.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import os.path
import tempfile
import warnings
import scilogger
import scisave
import pypeec

# crash on warnings and ignore deprecation
warnings.filterwarnings("error")
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=PendingDeprecationWarning)

# disable logging
scilogger.disable()

# get the path the folder
PATH_ROOT = os.path.dirname(__file__)


def _create_temp_file():
    """
    Get a temporary file.
    """

    (_, filename) = tempfile.mkstemp(suffix=".mpk")

    return filename


def _delete_temp_file(filename):
    """
    Delete a temporary file.
    """

    try:
        os.remove(filename)
    except OSError:
        pass


def _get_run_mesher(use_script, file_geometry, file_voxel):
    """
    Run the mesher.
    """

    if use_script:
        status = pypeec.run_arguments(
            [
                "--quiet",
                "mesher",
                "--geometry",
                file_geometry,
                "--voxel",
                file_voxel,
            ]
        )
        if status != 0:
            raise RuntimeError("invalid return code for the mesher")
    else:
        pypeec.run_mesher_file(
            file_geometry=file_geometry,
            file_voxel=file_voxel,
        )


def _get_run_solver(use_script, file_problem, file_tolerance, file_voxel, file_solution):
    """
    Run the solver.
    """

    if use_script:
        status = pypeec.run_arguments(
            [
                "--quiet",
                "solver",
                "--voxel",
                file_voxel,
                "--problem",
                file_problem,
                "--tolerance",
                file_tolerance,
                "--solution",
                file_solution,
            ]
        )
        if status != 0:
            raise RuntimeError("invalid return code for the solver")
    else:
        pypeec.run_solver_file(
            file_voxel=file_voxel,
            file_problem=file_problem,
            file_tolerance=file_tolerance,
            file_solution=file_solution,
        )


def _get_run_viewer(use_script, file_viewer, file_voxel):
    """
    Run the viewer.
    """

    if use_script:
        status = pypeec.run_arguments(
            [
                "--quiet",
                "viewer",
                "--voxel",
                file_voxel,
                "--viewer",
                file_viewer,
                "--plot_mode",
                "debug",
            ]
        )
        if status != 0:
            raise RuntimeError("invalid return code for the viewer")
    else:
        pypeec.run_viewer_file(
            file_voxel=file_voxel,
            file_viewer=file_viewer,
            plot_mode="debug",
        )


def _get_run_plotter(use_script, file_plotter, file_solution):
    """
    Run the plotter.
    """

    if use_script:
        status = pypeec.run_arguments(
            [
                "--quiet",
                "plotter",
                "--solution",
                file_solution,
                "--plotter",
                file_plotter,
                "--plot_mode",
                "debug",
            ]
        )
        if status != 0:
            raise RuntimeError("invalid return code for the plotter")
    else:
        pypeec.run_plotter_file(
            file_solution=file_solution,
            file_plotter=file_plotter,
            plot_mode="debug",
        )


def run_workflow(name, use_script):
    """
    Run the complete workflow:
        - Run the mesher.
        - Run the solver.
        - Run the viewer.
        - Run the plotter.

    The intermediate file are stored with temporary files.
    The temporary files are deleted at the end of the function.

    The workflow can be run with two modes:
        - With the command line script (pypeec.script).
        - With the API (pypeec.main).
    """

    # construct the folder path for the examples
    folder_examples = os.path.join(PATH_ROOT, "..", "..", "examples")

    # get input file name
    file_geometry = os.path.join(folder_examples, name, "geometry.yaml")
    file_problem = os.path.join(folder_examples, name, "problem.yaml")

    # get config file name
    file_plotter = os.path.join(folder_examples, "config", "plotter.yaml")
    file_viewer = os.path.join(folder_examples, "config", "viewer.yaml")
    file_tolerance = os.path.join(folder_examples, "config", "tolerance.yaml")

    # get the temporary files
    file_voxel = _create_temp_file()
    file_solution = _create_temp_file()

    # run the workflow and load the results
    try:
        # run the workflow
        _get_run_mesher(use_script, file_geometry, file_voxel)
        _get_run_solver(use_script, file_problem, file_tolerance, file_voxel, file_solution)
        _get_run_plotter(use_script, file_plotter, file_solution)
        _get_run_viewer(use_script, file_viewer, file_voxel)

        # load the files
        data_voxel = scisave.load_data(file_voxel)
        data_solution = scisave.load_data(file_solution)
    finally:
        # delete the temporary files
        _delete_temp_file(file_voxel)
        _delete_temp_file(file_solution)

    return data_voxel, data_solution
