"""
Main script for creating a 3D voxel structure.
Check the input data and mesh the structure.
The different parts of the code are timed.

Three different kind of geometry can be meshed:
    - stl: the voxel structure is generated from 3D STL files
    - png: the voxel structure is generated from stacked PNG images
    - shape: the voxel structure is generated from stacked 2D vector shapes
    - voxel: the voxel structure is given with the voxel indices

The mesher is implemented with PyVista, Pillow, Shapely, and Rasterio.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

from pypeec.lib_mesher import mesher_voxel
from pypeec.lib_mesher import mesher_shape
from pypeec.lib_mesher import mesher_png
from pypeec.lib_mesher import mesher_stl
from pypeec.lib_mesher import voxel_conflict
from pypeec.lib_mesher import voxel_resample
from pypeec.lib_mesher import voxel_connection
from pypeec.lib_mesher import voxel_summary
from pypeec.lib_check import check_data_geometry
from pypeec.lib_check import check_data_options
from pypeec import log
from pypeec.error import CheckError, RunError

# get a logger
LOGGER = log.get_logger("MESHER")


def _run_mesher(data_geometry):
    """
    Run the mesher
    """

    # extract the input data
    mesh_type = data_geometry["mesh_type"]
    data_voxelize = data_geometry["data_voxelize"]

    # voxelize the geometry
    if mesh_type == "voxel":
        (reference, data_internal) = _run_voxel(data_voxelize)
    elif mesh_type == "shape":
        (reference, data_internal) = _run_shape(data_voxelize)
    elif mesh_type == "png":
        (reference, data_internal) = _run_png(data_voxelize)
    elif mesh_type == "stl":
        (reference, data_internal) = _run_stl(data_voxelize)
    else:
        raise CheckError("invalid mesh type")

    return reference, data_internal


def _run_voxel(data_voxelize):
    """
    Generate a 3D voxel structure from indices.
    """

    # extract the data
    param = data_voxelize["param"]
    domain_index = data_voxelize["domain_index"]

    # process the indices arrays
    with log.BlockTimer(LOGGER, "mesher_voxel"):
        (n, d, c, domain_def, reference) = mesher_voxel.get_mesh(param, domain_index)

    # assemble the data
    data_internal = {
        "n": n,
        "d": d,
        "c": c,
        "domain_def": domain_def,
    }

    return reference, data_internal


def _run_shape(data_voxelize):
    """
    Generate a 3D voxel structure from 2D vector shapes.
    """

    # extract the data
    param = data_voxelize["param"]
    layer_stack = data_voxelize["layer_stack"]
    geometry_shape = data_voxelize["geometry_shape"]

    # process the shapes
    with log.BlockTimer(LOGGER, "mesher_shape"):
        (n, d, c, domain_def, reference) = mesher_shape.get_mesh(param, layer_stack, geometry_shape)

    # assemble the data
    data_internal = {
        "n": n,
        "d": d,
        "c": c,
        "domain_def": domain_def,
    }

    return reference, data_internal


def _run_png(data_voxelize):
    """
    Generate a 3D voxel structure from PNG images.
    """

    # extract the data
    param = data_voxelize["param"]
    domain_color = data_voxelize["domain_color"]
    layer_stack = data_voxelize["layer_stack"]

    # voxelize the PNG files
    with log.BlockTimer(LOGGER, "mesher_png"):
        (n, d, c, domain_def, reference) = mesher_png.get_mesh(param, domain_color, layer_stack)

    # assemble the data
    data_internal = {
        "n": n,
        "d": d,
        "c": c,
        "domain_def": domain_def,
    }

    return reference, data_internal


def _run_stl(data_voxelize):
    """
    Generate a 3D voxel structure from 3D STL files.
    """

    # extract the data
    param = data_voxelize["param"]
    domain_stl = data_voxelize["domain_stl"]

    # voxelize the STL files
    with log.BlockTimer(LOGGER, "mesher_stl"):
        (n, d, c, domain_def, reference) = mesher_stl.get_mesh(param, domain_stl)

    # assemble the data
    data_internal = {
        "n": n,
        "d": d,
        "c": c,
        "domain_def": domain_def,
    }

    return reference, data_internal


def _run_resample_graph(reference, data_internal, data_geometry, is_truncated):
    """
    Resampling of a 3D voxel structure (increases the number of voxels).
    """

    # extract the data
    resampling = data_geometry["resampling"]
    check_conflict = data_geometry["check_conflict"]
    check_connection = data_geometry["check_connection"]
    domain_connection = data_geometry["domain_connection"]
    domain_conflict = data_geometry["domain_conflict"]

    # extract the data
    n = data_internal["n"]
    d = data_internal["d"]
    c = data_internal["c"]
    domain_def = data_internal["domain_def"]

    if check_conflict:
        with log.BlockTimer(LOGGER, "voxel_conflict"):
            domain_def = voxel_conflict.get_conflict(domain_def, domain_conflict)

    with log.BlockTimer(LOGGER, "voxel_resample"):
        (n, d, c, s, domain_def) = voxel_resample.get_remesh(n, d, c, domain_def, resampling)

    if check_connection:
        with log.BlockTimer(LOGGER, "voxel_connection"):
            connection_def = voxel_connection.get_connection(n, domain_def, domain_connection)
    else:
        connection_def = []

    with log.BlockTimer(LOGGER, "voxel_summary"):
        voxel_status = voxel_summary.get_status(n, d, s, c, domain_def, connection_def)

    # assemble the data
    data_geom = {
        "n": n,
        "d": d,
        "s": s,
        "c": c,
        "voxel_status": voxel_status,
    }

    # if required, add the complete data
    if not is_truncated:
        data_add = {
            "domain_def": domain_def,
            "connection_def": connection_def,
            "reference": reference,
        }
        data_geom = {**data_geom, **data_add}

    return data_geom


def _get_data(ex, data_geom, timestamp, is_truncated):
    """
    Assemble the returned data.
    """

    # end message
    (duration, fmt) = log.get_duration(timestamp)

    if ex is None:
        status = True
        LOGGER.info("duration: %s" % fmt)
        LOGGER.info("successful termination")
    else:
        log.log_exception(LOGGER, ex)
        LOGGER.error("duration: %s" % fmt)
        LOGGER.error("invalid termination")
        status = False

    # extract the solution
    data_voxel = {
        "ex": ex,
        "status": status,
        "duration": duration,
        "is_truncated": is_truncated,
        "data_geom": data_geom,
    }

    return status, ex, data_voxel


def run(data_geometry, is_truncated=False):
    """
    Main script for meshing the geometry and generating a 3D voxel structure.
    Handle invalid data with exceptions.
    """

    # get timestamp
    timestamp = log.get_timer()

    # run the code
    try:
        # check the input data
        LOGGER.info("check the input data")
        check_data_geometry.check_data_geometry(data_geometry)
        check_data_options.check_data_options(is_truncated)

        # run the mesher
        (reference, data_internal) = _run_mesher(data_geometry)

        # resample and assemble
        data_geom = _run_resample_graph(reference, data_internal, data_geometry, is_truncated)
    except (CheckError, RunError) as ex_local:
        (status, ex, data_voxel) = _get_data(ex_local, None, timestamp, is_truncated)
    else:
        (status, ex, data_voxel) = _get_data(None, data_geom, timestamp, is_truncated)

    return status, ex, data_voxel
