"""
Module for running the PyPEEC workflow.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import os.path
import tempfile
import logging
import warnings
from pypeec import main
from pypeec import script
from pypeec import io

# crash on warnings (except for deprecation warnings)
warnings.filterwarnings("error")
warnings.filterwarnings("ignore", category=DeprecationWarning)

# disable logging to prevent clutter during test evaluation
logging.disable(logging.INFO)

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

    status = script.run_arguments(argv)
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
            argv_me = ["me", "-ge", file_geometry, "-vo", file_voxel]
            argv_vi = ["vi", "-vo", file_voxel,  "-vi", file_viewer, "-pm", "none"]
            argv_so = ["so", "-vo", file_voxel,  "-pr", file_problem, "-to", file_tolerance, "-so", file_solution]
            argv_pl = ["pl", "-so", file_solution,  "-pl", file_plotter, "-pm", "none"]

            # run the scripts
            _run_script(argv_me)
            _run_script(argv_vi)
            _run_script(argv_so)
            _run_script(argv_pl)
        else:
            main.run_mesher_file(file_geometry, file_voxel)
            main.run_viewer_file(file_voxel, file_viewer, plot_mode="none")
            main.run_solver_file(file_voxel, file_problem, file_tolerance, file_solution)
            main.run_plotter_file(file_solution, file_plotter, plot_mode="none")

        # load the files
        data_voxel = io.load_data(file_voxel)
        data_solution = io.load_data(file_solution)
    finally:
        # close the temporary files
        _delete_temp_file(file_voxel)
        _delete_temp_file(file_solution)

    return data_voxel, data_solution
