"""
Module containing the program entry points.
    - Used for calling the mesher, solver, viewer, and plotter.
    - Files can be used for the input and output data.
    - Data structure can be used for the input and output data.
    - The import statements for the different modules are located inside the code.
    - This allows for a minimization of the loaded dependencies.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import sys
import shutil
import importlib.resources
from pypeec import config
from pypeec import log
from pypeec import io
from pypeec.error import FileError

# create the logger
LOGGER = log.get_logger("MAIN")

# get the logo display status
DISPLAY_LOGO = config.DISPLAY_LOGO

# init the logo display status
STATUS_LOGO = False


def run_display_logo():
    """
    Display the logo as a splash screen
    """

    # variable with the logo status
    global STATUS_LOGO

    # display the logo
    if not STATUS_LOGO:
        try:
            with importlib.resources.open_text("pypeec.data", "pypeec.txt") as file_logo:
                data = file_logo.read()
                print("", flush=True, file=sys.stderr)
                print(data, flush=True, file=sys.stderr)
                print("", flush=True, file=sys.stderr)
        except UnicodeError:
            pass

    # logo has been displayed
    STATUS_LOGO = True


def run_hide_logo():
    """
    Prevent the display of the splash screen.
    """

    # variable with the logo status
    global STATUS_LOGO

    # logo should not be displayed
    STATUS_LOGO = True


def run_extract(data_name, is_zip, path_extract):
    """
    Extract data (config, examples, or documentation).

    Parameters
    ----------
    data_name : string
        Name of the file containing the data.
    is_zip : boolean
        Indicate if the data is a zip archive.
    path_extract : string
        Path where the data will be extracted.
    """

    # display logo
    if DISPLAY_LOGO:
        run_display_logo()

    LOGGER.info("data extraction")
    try:
        with importlib.resources.path("pypeec.data", data_name) as file_data:
            if is_zip:
                shutil.unpack_archive(file_data, path_extract)
            else:
                shutil.copy(file_data, path_extract)
    except OSError as ex:
        log.log_exception(LOGGER, ex)
        LOGGER.error("invalid termination")
        raise ex
    else:
        LOGGER.info("successful termination")


def run_mesher_data(data_geometry, **kwargs):
    """
    Main script for meshing the geometry and generating a 3D voxel structure.
        - Get the geometry data as an argument.
        - Return the created voxel data.

    Parameters
    ----------
    data_geometry : data
        The dict describes the geometry, meshing and resampling process.
    is_truncated : boolean
        If false, the complete results are returned (default).
        If true, the results are truncated to save space.
        This argument is optional.

    Returns
    -------
    data_voxel : data
        The dict describes the voxel structure.
    """

    # display logo
    if DISPLAY_LOGO:
        run_display_logo()

    # load the tool
    LOGGER.info("load the mesher")
    from pypeec.run import mesher

    # run the tool
    LOGGER.info("run the mesher")
    data_voxel = mesher.run(data_geometry, **kwargs)

    return data_voxel


def run_mesher_file(file_geometry, file_voxel, **kwargs):
    """
    Main script for meshing the geometry and generating a 3D voxel structure.
        - Load the geometry data from a file.
        - Write the created voxel data in a file.

    Parameters
    ----------
    file_geometry : filename
        The file content describes the geometry, meshing and resampling process.
        This input file is loaded by this function (JSON or YAML format).
    file_voxel :  filename
        The file content describes the voxel structure.
        This output file is written by this function (Pickle format).
    is_truncated : boolean
        If false, the complete results are returned (default).
        If true, the results are truncated to save space.
        This argument is optional.
    """

    # display logo
    if DISPLAY_LOGO:
        run_display_logo()

    # load data
    try:
        LOGGER.info("load the input data")
        data_geometry = io.load_config(file_geometry)
    except FileError as ex:
        log.log_exception(LOGGER, ex)
        raise ex

    # call the mesher
    data_voxel = run_mesher_data(data_geometry, **kwargs)

    # save results
    try:
        LOGGER.info("save the results")
        io.write_pickle(file_voxel, data_voxel)
    except FileError as ex:
        log.log_exception(LOGGER, ex)
        raise ex


def run_viewer_data(data_voxel, data_point, data_viewer, **kwargs):
    """
    Main script for visualizing a 3D voxel structure.
        - Get the voxel data as an argument.
        - Get the point data as an argument.
        - Get the viewer data as an argument.

    Parameters
    ----------
    data_voxel : data
        The dict describes the voxel structure.
    data_point: data
        The array describes the point cloud used for field evaluation.
    data_viewer: data
        The dict describes the different plots to be created.
    tag_plot : list
        The list describes plots to be shown.
        If None, all the plots are shown (default).
        This argument is optional.
    plot_mode : string
        If "qt", the Qt framework is used for the rendering (default).
        If "nb", the plots are rendered within the Jupyter notebook.
        If "save", the plots are not shown but saved as screenshots.
        If "none", the plots are not shown (test mode).
        This argument is optional.
    folder : string
        Folder name for saving the screenshots.
        The current directory is used as the default directory.
        This argument is optional.
    name : string
        Prepended at the beginning of the screenshot filenames.
        This argument is optional.
    """

    # display logo
    if DISPLAY_LOGO:
        run_display_logo()

    # load the tool
    LOGGER.info("load the viewer")
    from pypeec.run import viewer

    # run the tool
    LOGGER.info("run the viewer")
    viewer.run(data_voxel, data_point, data_viewer, **kwargs)


def run_viewer_file(file_voxel, file_point, file_viewer, **kwargs):
    """
    Main script for visualizing a 3D voxel structure.
        - Load the voxel data from a file.
        - Load the point data from a file.
        - Load the viewer data from a file.

    Parameters
    ----------
    file_voxel : filename
        The file content describes the voxel structure.
        This input file is loaded by this function (Pickle format).
    file_point: filename
        The file content describes the point cloud used for field evaluation.
        This input file is loaded by this function (JSON or YAML format).
    file_viewer: filename
        The file content describes the different plots to be created.
        This input file is loaded by this function (JSON or YAML format).
    tag_plot : list
        The list describes plots to be shown.
        If None, all the plots are shown (default).
        This argument is optional.
    plot_mode : string
        If "qt", the Qt framework is used for the rendering (default).
        If "nb", the plots are rendered within the Jupyter notebook.
        If "save", the plots are not shown but saved as screenshots.
        If "none", the plots are not shown (test mode).
        This argument is optional.
    folder : string
        Folder name for saving the screenshots.
        The current directory is used as the default directory.
        This argument is optional.
    name : string
        Prepended at the beginning of the screenshot filenames.
        This argument is optional.
    """

    # display logo
    if DISPLAY_LOGO:
        run_display_logo()

    # load data
    try:
        LOGGER.info("load the input data")
        data_voxel = io.load_pickle(file_voxel)
        data_point = io.load_config(file_point)
        data_viewer = io.load_config(file_viewer)
    except FileError as ex:
        log.log_exception(LOGGER, ex)
        raise ex

    # call the viewer
    run_viewer_data(data_voxel, data_point, data_viewer, **kwargs)


def run_solver_data(data_voxel, data_problem, data_tolerance, **kwargs):
    """
    Main script for solving a problem with the PEEC solver.
        - Get the voxel data as an argument.
        - Get the problem data as an argument.
        - Get the tolerance data as an argument.
        - Return the created solution data.

    Parameters
    ----------
    data_voxel :  data
        The dict describes the voxel structure.
    data_problem: data
        The dict describes the problem to be solved.
    data_tolerance: data
        The dict describes the numerical options.
    is_truncated : boolean
        If false, the complete results are returned (default).
        If true, the results are truncated to save space.
        This argument is optional.

    Returns
    -------
    data_solution : data
        The dict describes the problem solution.
    """

    # display logo
    if DISPLAY_LOGO:
        run_display_logo()

    # load the tool
    LOGGER.info("load the solver")
    from pypeec.run import solver

    # run the tool
    LOGGER.info("run the solver")
    data_solution = solver.run(data_voxel, data_problem, data_tolerance, **kwargs)

    return data_solution


def run_solver_file(file_voxel, file_problem, file_tolerance, file_solution, **kwargs):
    """
    Main script for solving a problem with the PEEC solver.
        - Load the voxel data from a file.
        - Load the problem data from a file.
        - Load the tolerance data from a file.
        - Write the created solution data in a file.

    Parameters
    ----------
    file_voxel :  filename
        The file content describes the voxel structure.
        This input file is loaded by this function (Pickle format).
    file_problem: filename
        The file content describes the problem to be solved.
        This input file is loaded by this function (JSON or YAML format).
    file_tolerance: filename
        The file content describes the numerical options.
        This input file is loaded by this function (JSON or YAML format).
    file_solution :  filename
        The file content describes the problem solution.
        This output file is written by this function (Pickle format).
    is_truncated : boolean
        If false, the complete results are returned (default).
        If true, the results are truncated to save space.
        This argument is optional.
    """

    # display logo
    if DISPLAY_LOGO:
        run_display_logo()

    # load data
    try:
        LOGGER.info("load the input data")
        data_voxel = io.load_pickle(file_voxel)
        data_problem = io.load_config(file_problem)
        data_tolerance = io.load_config(file_tolerance)
    except FileError as ex:
        log.log_exception(LOGGER, ex)
        raise ex

    # call the solver
    data_solution = run_solver_data(data_voxel, data_problem, data_tolerance, **kwargs)

    # save results
    try:
        LOGGER.info("save the results")
        io.write_pickle(file_solution, data_solution)
    except FileError as ex:
        log.log_exception(LOGGER, ex)
        raise ex


def run_plotter_data(data_solution, data_point, data_plotter, **kwargs):
    """
    Main script for plotting the solution of a PEEC problem.
        - Get the solution data as an argument.
        - Get the point data as an argument.
        - Get the plotter data as an argument.

    Parameters
    ----------
    data_solution : data
        The dict describes the problem solution.
    data_point : data
        The array describes the point cloud used for field evaluation.
    data_plotter : data
        The dict describes the different plots to be created.
    tag_sweep : list
        The list describes sweeps to be shown.
        If None, all the sweeps are shown (default).
        This argument is optional.
    tag_plot : list
        The list describes plots to be shown.
        If None, all the plots are shown (default).
        This argument is optional.
    plot_mode : string
        If "qt", the Qt framework is used for the rendering (default).
        If "nb", the plots are rendered within the Jupyter notebook.
        If "save", the plots are not shown but saved as screenshots.
        If "none", the plots are not shown (test mode).
        This argument is optional.
    folder : string
        Folder name for saving the screenshots.
        The current directory is used as the default directory.
        This argument is optional.
    name : string
        Prepended at the beginning of the screenshot filenames.
        This argument is optional.
    """

    # display logo
    if DISPLAY_LOGO:
        run_display_logo()

    # load the tool
    LOGGER.info("load the plotter")
    from pypeec.run import plotter

    # run the tool
    LOGGER.info("run the plotter")
    plotter.run(data_solution, data_point, data_plotter, **kwargs)


def run_plotter_file(file_solution, file_point, file_plotter, **kwargs):
    """
    Main script for plotting the solution of a PEEC problem.
        - Load the solution data from a file.
        - Load the point data from a file.
        - Load the plotter data from a file.

    Parameters
    ----------
    file_solution : filename
        The dict describes the problem solution.
        This input file is loaded by this function (Pickle format).
    file_point : filename
        The array describes the point cloud used for field evaluation.
        This input file is loaded by this function (JSON or YAML format).
    file_plotter : filename
        The dict describes the different plots to be created.
        This input file is loaded by this function (JSON or YAML format).
    tag_sweep : list
        The list describes sweeps to be shown.
        If None, all the sweeps are shown (default).
        This argument is optional.
    tag_plot : list
        The list describes plots to be shown.
        If None, all the plots are shown (default).
        This argument is optional.
    plot_mode : string
        If "qt", the Qt framework is used for the rendering (default).
        If "nb", the plots are rendered within the Jupyter notebook.
        If "save", the plots are not shown but saved as screenshots.
        If "none", the plots are not shown (test mode).
        This argument is optional.
    folder : string
        Folder name for saving the screenshots.
        The current directory is used as the default directory.
        This argument is optional.
    name : string
        Prepended at the beginning of the screenshot filenames.
        This argument is optional.
    """

    # display logo
    if DISPLAY_LOGO:
        run_display_logo()

    # load data
    try:
        # load data
        LOGGER.info("load the input data")
        data_solution = io.load_pickle(file_solution)
        data_point = io.load_config(file_point)
        data_plotter = io.load_config(file_plotter)
    except FileError as ex:
        log.log_exception(LOGGER, ex)
        raise ex

    # call the plotter
    run_plotter_data(data_solution, data_point, data_plotter, **kwargs)
