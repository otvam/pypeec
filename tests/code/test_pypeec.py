"""
Module for running the PyPEEC workflow.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import os.path
import tempfile
import warnings
import logging
import scisave
import pypeec

# disable logging to prevent clutter during test evaluation
logging.disable(logging.CRITICAL)

# get the path the folder
PATH_ROOT = os.path.dirname(__file__)

# construct the config folder path
FOLDER_EXAMPLES = os.path.join(PATH_ROOT, "..", "..", "examples")


def _create_temp_file():
    """
    Get a temporary file.
    """

    (_, filename) = tempfile.mkstemp(suffix=".gz")

    return filename


def _delete_temp_file(filename):
    """
    Delete a temporary file.
    """

    try:
        os.remove(filename)
    except OSError:
        pass


def _run_script(argv):
    """
    Run the command line script with arguments.
    """

    status = pypeec.run_arguments(argv)
    if status != 0:
        raise RuntimeError("invalid return code for the script")


def run_workflow(name, use_script):
    """
    Run the complete workflow:
        - run the mesher
        - run the viewer
        - run the solver
        - run the plotter

    The intermediate file are stored with temporary files.
    The temporary files are deleted at the end of the function.

    The workflow can be run with two modes:
        - with the command line script (pypeec.script)
        - with the API (pypeec.main)
    """

    # crash on warnings and ignore deprecation
    warnings.filterwarnings("error")
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", category=PendingDeprecationWarning)

    # get input file name
    file_geometry = os.path.join(FOLDER_EXAMPLES, name, "geometry.yaml")
    file_problem = os.path.join(FOLDER_EXAMPLES, name, "problem.yaml")

    # get config file name
    file_plotter = os.path.join(FOLDER_EXAMPLES, "config", "plotter.yaml")
    file_viewer = os.path.join(FOLDER_EXAMPLES, "config", "viewer.yaml")
    file_tolerance = os.path.join(FOLDER_EXAMPLES, "config", "tolerance.yaml")

    # get the temporary files
    file_voxel = _create_temp_file()
    file_solution = _create_temp_file()

    # run the code
    try:
        # run the workflow
        if use_script:
            # get the arguments
            argv_me = ["-q", "me", "-ge", file_geometry, "-vo", file_voxel]
            argv_vi = ["-q", "vi", "-vo", file_voxel,  "-vi", file_viewer, "-pm", "none"]
            argv_so = ["-q", "so", "-vo", file_voxel,  "-pr", file_problem, "-to", file_tolerance, "-so", file_solution]
            argv_pl = ["-q", "pl", "-so", file_solution,  "-pl", file_plotter, "-pm", "none"]

            # run the scripts
            _run_script(argv_me)
            _run_script(argv_vi)
            _run_script(argv_so)
            _run_script(argv_pl)
        else:
            pypeec.run_mesher_file(file_geometry, file_voxel)
            pypeec.run_viewer_file(file_voxel, file_viewer, plot_mode="none")
            pypeec.run_solver_file(file_voxel, file_problem, file_tolerance, file_solution)
            pypeec.run_plotter_file(file_solution, file_plotter, plot_mode="none")

        # load the files
        data_voxel = scisave.load_data(file_voxel)
        data_solution = scisave.load_data(file_solution)
    finally:
        # close the temporary files
        _delete_temp_file(file_voxel)
        _delete_temp_file(file_solution)

    return data_voxel, data_solution
