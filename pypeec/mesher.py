"""
Main script for creating a 3D voxel structure.
Check the input data and mesh the structure.
The different parts of the code are timed.

Three different kind of geometry can be meshed:
    - png: the voxel are taken from 2D PNG images and assembled into a 3D voxel structures
    - stl: the voxel structure is generated from 3D STL files
    - voxel: the voxel structure is provided (do nothing)

The mesher is implemented with PyVista.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

from pypeec.lib_mesher import png_mesher
from pypeec.lib_mesher import stl_mesher
from pypeec.lib_mesher import voxel_resample
from pypeec.lib_mesher import voxel_connection
from pypeec.lib_mesher import voxel_summary
from pypeec.lib_check import check_data_mesher
from pypeec.lib_utils import timelogger
from pypeec.error import CheckError, RunError

# get a logger
logger = timelogger.get_logger("MESHER")


def _run_mesher(data_mesher, path_ref):
    """
    Run the mesher
    """

    # extract the input data
    mesh_type = data_mesher["mesh_type"]
    data_voxelize = data_mesher["data_voxelize"]

    # voxelize the geometry
    if mesh_type == "voxel":
        reference = None
        data_voxel = data_voxelize
    elif mesh_type == "png":
        reference = None
        data_voxel = _run_png(data_voxelize, path_ref)
    elif mesh_type == "stl":
        (reference, data_voxel) = _run_stl(data_voxelize, path_ref)
    else:
        raise CheckError("invalid mesh type")

    return reference, data_voxel


def _run_png(data_voxelize, path_ref):
    """
    Generate a 3D voxel structure from 2D PNG images.
    """

    # extract the data
    d = data_voxelize["d"]
    c = data_voxelize["c"]
    nx = data_voxelize["nx"]
    ny = data_voxelize["ny"]
    domain_color = data_voxelize["domain_color"]
    layer_stack = data_voxelize["layer_stack"]

    # get the voxel geometry and the incidence matrix
    with timelogger.BlockTimer(logger, "png_mesher"):
        layer_stack = check_data_mesher.get_layer_stack_path(layer_stack, path_ref)
        (n, domain_def) = png_mesher.get_mesh(nx, ny, domain_color, layer_stack)

    # assemble the data
    data_voxel = {
        "n": n,
        "d": d,
        "c": c,
        "domain_def": domain_def,
    }

    return data_voxel


def _run_stl(data_voxelize, path_ref):
    """
    Generate a 3D voxel structure from 3D STL files.
    """

    # extract the data
    n = data_voxelize["n"]
    d = data_voxelize["d"]
    c = data_voxelize["c"]
    sampling = data_voxelize["sampling"]
    pts_min = data_voxelize["pts_min"]
    pts_max = data_voxelize["pts_max"]
    domain_stl = data_voxelize["domain_stl"]
    domain_conflict = data_voxelize["domain_conflict"]

    # get the voxel geometry and the incidence matrix
    with timelogger.BlockTimer(logger, "stl_mesher"):
        domain_stl = check_data_mesher.get_domain_stl_path(domain_stl, path_ref)
        (n, d, c, domain_def, reference) = stl_mesher.get_mesh(n, d, c, sampling, pts_min, pts_max, domain_stl)
        domain_def = stl_mesher.get_conflict(domain_def, domain_conflict)

    # assemble the data
    data_voxel = {
        "n": n,
        "d": d,
        "c": c,
        "domain_def": domain_def,
    }

    return reference, data_voxel


def _run_resample_graph(reference, data_voxel, data_mesher):
    """
    Resampling of a 3D voxel structure (increases the number of voxels).
    """

    # extract the data
    resampling_factor = data_mesher["resampling_factor"]
    domain_connection = data_mesher["domain_connection"]

    # extract the data
    n = data_voxel["n"]
    d = data_voxel["d"]
    c = data_voxel["c"]
    domain_def = data_voxel["domain_def"]

    with timelogger.BlockTimer(logger, "voxel_resample"):
        (n, d, domain_def) = voxel_resample.get_remesh(n, d, domain_def, resampling_factor)

    with timelogger.BlockTimer(logger, "voxel_connection"):
        connection_def = voxel_connection.get_connection(n, domain_def, domain_connection)

    with timelogger.BlockTimer(logger, "voxel_summary"):
        voxel_status = voxel_summary.get_status(n, d, c, domain_def, connection_def)

    # assemble the data
    data_voxel = {
        "n": n,
        "d": d,
        "c": c,
        "domain_def": domain_def,
        "connection_def": connection_def,
        "voxel_status": voxel_status,
        "reference": reference,
    }

    return data_voxel


def run(data_mesher, path_ref):
    """
    Main script for meshing the geometry and generating a 3D voxel structure.
    Handle invalid data with exceptions.

    Parameters
    ----------
    data_mesher : dict
        The dict describes the meshing and resampling process.
        The voxel structure can be explicitly given or generated from PNG or STL files.
    path_ref :  path (string or None)
        Path used to load the PNG and STL files.
        If None, the filename specified in the mesher data are used directly.
        If a string is given, the path is used to find the location of the files.

    Returns
    -------
    status : boolean
        True if the call is successful.
        False if the problems are encountered.
    data_voxel: dict
        The dict describes the voxel structure.
        The voxel grid (number, size, and origin) is defined.
        Different domains (with the indices of the voxel) are defined.
        The connected components of the graph defined by the voxel structure are defined.
    ex : exception
        The encountered exception (if any).
        None if the termination is successful.
    """

    # run the code
    try:
        # check the input data
        logger.info("check the input data")
        check_data_mesher.check_data_mesher(data_mesher)

        # run the mesher
        (reference, data_voxel) = _run_mesher(data_mesher, path_ref)

        # resample and assemble
        data_voxel = _run_resample_graph(reference, data_voxel, data_mesher)
    except (CheckError, RunError) as ex:
        timelogger.log_exception(logger, ex)
        return False, None, ex

    # end message
    logger.info("successful termination")

    return True, data_voxel, None
