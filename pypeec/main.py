"""
Module containing the program entry points.
    - Used for calling the mesher, solver, viewer, and plotter.
    - Files can be used for the input and output data.
    - Data structure can be used for the input and output data.

The import statements for the different modules are located inside the code.
This allows for a minimization of the loaded dependencies.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import shutil
import scisave
import scilogger
import importlib.resources
import pypeec

# create the logger
LOGGER = scilogger.get_logger(__name__, "pypeec")


def _run_extract_archive(filename, path):
    """
    Extract an archive from the package data (examples,or documentation).
    """

    # init
    LOGGER.info("data extraction: start")

    # execute workflow
    LOGGER.info("data extraction: extract")
    try:
        folder = importlib.resources.files("pypeec.data")
        with importlib.resources.as_file(folder.joinpath(filename)) as fid:
            shutil.unpack_archive(fid, path, format="xztar")
    except FileNotFoundError:
        raise RuntimeError("archive not found: %s" % filename) from None
    except OSError:
        raise RuntimeError("extraction failed: %s" % path) from None

    # teardown
    LOGGER.info("data extraction: finished")


def _create_data(layout, timestamp, data):
    """
    Create an output data structure.
    """

    # get timing information
    (seconds, duration, date) = scilogger.get_duration(timestamp)

    # construct the metadata
    meta = {
        "name": pypeec.__name__,
        "version": pypeec.__version__,
        "layout": layout,
        "date": date,
        "duration": duration,
        "seconds": seconds,
    }

    # assemble the output data
    data_out = {
        "meta": meta,
        "data": data,
    }

    return data_out


def _load_data(layout_out, data_out):
    """
    Load an output data structure.
    """

    # check the output data
    schema = {
        "type": "object",
        "required": [
            "meta",
            "data",
        ],
        "properties": {
            "meta": {"type": "object"},
            "data": {"type": "object"},
        },
    }
    scisave.validate_schema(data_out, schema)

    # extract the output data
    meta = data_out["meta"]
    data = data_out["data"]

    # check the metata
    schema = {
        "type": "object",
        "required": [
            "name",
            "version",
            "layout",
            "seconds",
            "duration",
            "date",
        ],
        "properties": {
            "meta": {"type": "string", "minLength": 1},
            "version": {"type": "string", "minLength": 1},
            "layout": {"type": "string", "minLength": 1},
            "date": {"type": "string", "minLength": 1},
            "duration": {"type": "string", "minLength": 1},
            "seconds": {"type": "number", "minimum": 0},
        },
    }
    scisave.validate_schema(meta, schema)

    # extract meta
    name = meta["name"]
    version = meta["version"]
    layout = meta["layout"]

    # check that the layout is correct
    if layout != layout_out:
        raise ValueError("invalid data format: %s" % layout)

    # display a warning in case of a version mismatch
    if (name != pypeec.__name__) or (version != pypeec.__version__):
        LOGGER.warning("invalid data version: %s / %s", name, version)

    return data


def run_mesher_data(data_geometry):
    """
    Function for meshing the geometry and generating a 3D voxel structure.
        - Get the geometry data as an argument.
        - Create a 3D voxel structure from the geometry.
        - Return the created voxel data.

    Parameters
    ----------
    data_geometry : data
        - The dict describes the geometry meshing and resampling process.

    Returns
    -------
    data_voxel : data
        - The dict describes the meshed voxel structure.
    """

    # execute workflow
    try:
        # load the tool
        LOGGER.info("load the mesher")
        from pypeec.run import mesher

        # run the tool
        LOGGER.info("run the mesher")
        data_voxel = mesher.run(data_geometry)
    except Exception as ex:
        LOGGER.log_exception(ex)
        LOGGER.error("invalid mesher termination")
        raise ex
    else:
        LOGGER.info("successful mesher termination")

    return data_voxel


def run_mesher_file(file_geometry, file_voxel):
    """
    Function for meshing the geometry and generating a 3D voxel structure.
        - Load the geometry data from a file.
        - Create a 3D voxel structure from the geometry.
        - Write the created voxel data in a file.

    Parameters
    ----------
    file_geometry : filename
        - The file content describes the geometry meshing and resampling process.
        - This input file is loaded by this function (JSON or YAML format).
    file_voxel : filename
        - The file content describes the meshed voxel structure.
        - This output file is created by the function (JSON or MessagePack or Pickle format).
    """

    # get timestamp
    timestamp = scilogger.get_timestamp()

    # load data
    try:
        LOGGER.info("load the input data : start")
        data_geometry = scisave.load_config(file_geometry)
        LOGGER.info("load the input data : done")
    except Exception as ex:
        LOGGER.log_exception(ex)
        raise ex

    # run the tool
    data_voxel = run_mesher_data(data_geometry)

    # save results
    try:
        LOGGER.info("save the results : start")
        data_voxel = _create_data("data_voxel", timestamp, data_voxel)
        scisave.write_data(file_voxel, data_voxel)
        LOGGER.info("save the results : done")
    except Exception as ex:
        LOGGER.log_exception(ex)
        raise ex


def run_viewer_data(data_voxel, data_viewer, **kwargs):
    """
    Function for visualizing a 3D voxel structure.
        - Get the voxel data as an argument.
        - Get the viewer data as an argument.
        - Visualize the 3D voxel structure.

    Parameters
    ----------
    data_voxel : data
        - The dict describes the meshed voxel structure.
    data_viewer: data
        - The dict describes the different plots to be created.
    tag_plot : list
        - The list describes the plots to be shown.
        - If None or omitted: all the plots are shown.
    plot_mode : string
        - If "qt", the Qt framework is used for rendering the plots.
        - If "nb_int", interactive plots are rendered within the Jupyter notebook.
        - If "nb_std", static plots are rendered within the Jupyter notebook.
        - If "png", the plot images are saved as PNG files.
        - If "vtk", the plot data are saved as VTK files.
        - If "debug", the plots are not shown (test mode).
        - If None or omitted: the debug mode is used.
    path : path
        - Path where the plots should be generated.
        - If None or omitted: the current directory is used.
    name : string
        - Prepended at the beginning of the screenshot filenames.
        - If None or omitted: the "pypeec" prefix is used.
    """

    # execute workflow
    try:
        # load the tool
        LOGGER.info("load the viewer")
        from pypeec.run import viewer

        # run the tool
        LOGGER.info("run the viewer")
        viewer.run(data_voxel, data_viewer, **kwargs)
    except Exception as ex:
        LOGGER.log_exception(ex)
        LOGGER.error("invalid viewer termination")
        raise ex
    else:
        LOGGER.info("successful viewer termination")


def run_viewer_file(file_voxel, file_viewer, **kwargs):
    """
    Function for visualizing a 3D voxel structure.
        - Load the voxel data from a file.
        - Load the viewer data from a file.
        - Visualize the 3D voxel structure.

    Parameters
    ----------
    file_voxel : filename
        - The file content describes the meshed voxel structure.
        - This input file is loaded by this function (JSON or MessagePack or Pickle format).
    file_viewer: filename
        - The file content describes the different plots to be created.
        - This input file is loaded by this function (JSON or YAML format).
    tag_plot : list
        - The list describes the plots to be shown.
        - If None or omitted: all the plots are shown.
    plot_mode : string
        - If "qt", the Qt framework is used for rendering the plots.
        - If "nb_int", interactive plots are rendered within the Jupyter notebook.
        - If "nb_std", static plots are rendered within the Jupyter notebook.
        - If "png", the plot images are saved as PNG files.
        - If "vtk", the plot data are saved as VTK files.
        - If "debug", the plots are not shown (test mode).
        - If None or omitted: the debug mode is used.
    path : path
        - Path where the plots should be generated.
        - If None or omitted: the current directory is used.
    name : string
        - Prepended at the beginning of the screenshot filenames.
        - If None or omitted: the "pypeec" prefix is used.
    """

    # load data
    try:
        LOGGER.info("load the input data : start")
        data_viewer = scisave.load_config(file_viewer)
        data_voxel = scisave.load_data(file_voxel)
        data_voxel = _load_data("data_voxel", data_voxel)
        LOGGER.info("load the input data : done")
    except Exception as ex:
        LOGGER.log_exception(ex)
        raise ex

    # run the tool
    run_viewer_data(data_voxel, data_viewer, **kwargs)


def run_solver_data(data_voxel, data_problem, data_tolerance):
    """
    Function for solving a problem with the PEEC solver.
        - Get the voxel data as an argument.
        - Get the problem data as an argument.
        - Get the tolerance data as an argument.
        - Solve the quasi-magnetostatic problem.
        - Return the created solution data.

    Parameters
    ----------
    data_voxel : data
        - The dict describes the meshed voxel structure.
    data_problem: data
        - The dict describes the problem to be solved.
    data_tolerance: data
        - The dict describes the numerical options.

    Returns
    -------
    data_solution : data
        - The dict describes the problem solution.
    """

    # execute workflow
    try:
        # load the tool
        LOGGER.info("load the solver")
        from pypeec.run import solver

        # run the tool
        LOGGER.info("run the solver")
        data_solution = solver.run(data_voxel, data_problem, data_tolerance)
    except Exception as ex:
        LOGGER.log_exception(ex)
        LOGGER.error("invalid solver termination")
        raise ex
    else:
        LOGGER.info("successful solver termination")

    return data_solution


def run_solver_file(file_voxel, file_problem, file_tolerance, file_solution):
    """
    Function for solving a problem with the PEEC solver.
        - Load the voxel data from a file.
        - Load the problem data from a file.
        - Load the tolerance data from a file.
        - Solve the quasi-magnetostatic problem.
        - Write the created solution data in a file.

    Parameters
    ----------
    file_voxel : filename
        - The file content describes the meshed voxel structure.
        - This input file is loaded by this function (JSON or MessagePack or Pickle format).
    file_problem: filename
        - The file content describes the problem to be solved.
        - This input file is loaded by this function (JSON or YAML format).
    file_tolerance: filename
        - The file content describes the numerical options.
        - This input file is loaded by this function (JSON or YAML format).
    file_solution : filename
        - The file content describes the problem solution.
        - This output file is created by the function (JSON or MessagePack or Pickle format).
    """

    # get timestamp
    timestamp = scilogger.get_timestamp()

    # load data
    try:
        LOGGER.info("load the input data : start")
        data_problem = scisave.load_config(file_problem)
        data_tolerance = scisave.load_config(file_tolerance)
        data_voxel = scisave.load_data(file_voxel)
        data_voxel = _load_data("data_voxel", data_voxel)
        LOGGER.info("load the input data : done")
    except Exception as ex:
        LOGGER.log_exception(ex)
        raise ex

    # run the tool
    data_solution = run_solver_data(data_voxel, data_problem, data_tolerance)

    # save results
    try:
        LOGGER.info("save the results : start")
        data_solution = _create_data("data_solution", timestamp, data_solution)
        scisave.write_data(file_solution, data_solution)
        LOGGER.info("save the results : done")
    except Exception as ex:
        LOGGER.log_exception(ex)
        raise ex


def run_plotter_data(data_solution, data_plotter, **kwargs):
    """
    Function for plotting the solution of a PEEC problem.
        - Get the solution data as an argument.
        - Get the plotter data as an argument.
        - Visualize the problem solution

    Parameters
    ----------
    data_solution : data
        - The dict describes the problem solution.
    data_plotter : data
        - The dict describes the different plots to be created.
    tag_sweep : list
        - The list describes the solver sweeps to be shown.
        - If None or omitted: all the sweeps are shown.
    tag_plot : list
        - The list describes the plots to be shown.
        - If None or omitted: all the plots are shown.
    plot_mode : string
        - If "qt", the Qt framework is used for rendering the plots.
        - If "nb_int", interactive plots are rendered within the Jupyter notebook.
        - If "nb_std", static plots are rendered within the Jupyter notebook.
        - If "png", the plot images are saved as PNG files.
        - If "vtk", the plot data are saved as VTK files.
        - If "debug", the plots are not shown (test mode).
        - If None or omitted: the debug mode is used.
    path : path
        - Path where the plots should be generated.
        - If None or omitted: the current directory is used.
    name : string
        - Prepended at the beginning of the screenshot filenames.
        - If None or omitted: the "pypeec" prefix is used.
    """

    # execute workflow
    try:
        # load the tool
        LOGGER.info("load the plotter")
        from pypeec.run import plotter

        # run the tool
        LOGGER.info("run the plotter")
        plotter.run(data_solution, data_plotter, **kwargs)
    except Exception as ex:
        LOGGER.log_exception(ex)
        LOGGER.error("invalid plotter termination")
        raise ex
    else:
        LOGGER.info("successful plotter termination")


def run_plotter_file(file_solution, file_plotter, **kwargs):
    """
    Function for plotting the solution of a PEEC problem.
        - Load the solution data from a file.
        - Load the plotter data from a file.
        - Visualize the problem solution

    Parameters
    ----------
    file_solution : filename
        - The dict describes the problem solution.
        - This input file is loaded by this function (JSON or MessagePack or Pickle format).
    file_plotter : filename
        - The dict describes the different plots to be created.
        - This input file is loaded by this function (JSON or YAML format).
    tag_sweep : list
        - The list describes the solver sweeps to be shown.
        - If None or omitted: all the sweeps are shown.
    tag_plot : list
        - The list describes the plots to be shown.
        - If None or omitted: all the plots are shown.
    plot_mode : string
        - If "qt", the Qt framework is used for rendering the plots.
        - If "nb_int", interactive plots are rendered within the Jupyter notebook.
        - If "nb_std", static plots are rendered within the Jupyter notebook.
        - If "png", the plot images are saved as PNG files.
        - If "vtk", the plot data are saved as VTK files.
        - If "debug", the plots are not shown (test mode).
        - If None or omitted: the debug mode is used.
    path : path
        - Path where the plots should be generated.
        - If None or omitted: the current directory is used.
    name : string
        - Prepended at the beginning of the screenshot filenames.
        - If None or omitted: the "pypeec" prefix is used.
    """

    # load data
    try:
        # load data
        LOGGER.info("load the input data : start")
        data_plotter = scisave.load_config(file_plotter)
        data_solution = scisave.load_data(file_solution)
        data_solution = _load_data("data_solution", data_solution)
        LOGGER.info("load the input data : done")
    except Exception as ex:
        LOGGER.log_exception(ex)
        raise ex

    # run the tool
    run_plotter_data(data_solution, data_plotter, **kwargs)


def run_extract_examples(path):
    """
    Function for extracting the PyPEEC examples.
        - Get a file system path as an argument.
        - Extract the data at the specified location.

    Parameters
    ----------
    path : path
        - Path where the data should be extracted.
    """

    # execute workflow
    try:
        _run_extract_archive("examples.tar.xz", path)
    except Exception as ex:
        LOGGER.log_exception(ex)
        raise ex


def run_extract_documentation(path):
    """
    Function for extracting the PyPEEC documentation.
        - Get a file system path as an argument.
        - Extract the data at the specified location.

    Parameters
    ----------
    path : path
        - Path where the data should be extracted.
    """

    # execute workflow
    try:
        _run_extract_archive("documentation.tar.xz", path)
    except Exception as ex:
        LOGGER.log_exception(ex)
        raise ex
