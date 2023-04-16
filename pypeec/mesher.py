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

from pypeec.lib_mesher import mesher_voxel
from pypeec.lib_mesher import mesher_png
from pypeec.lib_mesher import mesher_stl
from pypeec.lib_mesher import voxel_conflict
from pypeec.lib_mesher import voxel_resample
from pypeec.lib_mesher import voxel_connection
from pypeec.lib_mesher import voxel_summary
from pypeec.lib_check import check_data_geometry
from pypeec.lib_check import check_data_mesher
from pypeec import utils_log
from pypeec.error import CheckError, RunError

# get a logger
LOGGER = utils_log.get_logger("MESHER")


def _run_mesher(data_mesher):
    """
    Run the mesher
    """

    # extract the input data
    mesh_type = data_mesher["mesh_type"]
    data_voxelize = data_mesher["data_voxelize"]

    # voxelize the geometry
    if mesh_type == "voxel":
        reference = None
        data_voxel = _run_voxel(data_voxelize)
    elif mesh_type == "png":
        reference = None
        data_voxel = _run_png(data_voxelize)
    elif mesh_type == "stl":
        (reference, data_voxel) = _run_stl(data_voxelize)
    else:
        raise CheckError("invalid mesh type")

    return reference, data_voxel


def _run_voxel(data_voxelize):
    """
    Generate a 3D voxel structure from indices.
    """

    # extract the data
    n = data_voxelize["n"]
    d = data_voxelize["d"]
    c = data_voxelize["c"]
    domain_def = data_voxelize["domain_def"]

    # process the indices arrays
    with utils_log.BlockTimer(LOGGER, "mesher_voxel"):
        domain_def = mesher_voxel.get_mesh(n, domain_def)

    # assemble the data
    data_voxel = {
        "n": n,
        "d": d,
        "c": c,
        "domain_def": domain_def,
    }

    return data_voxel


def _run_png(data_voxelize):
    """
    Generate a 3D voxel structure from 2D PNG images.
    """

    # extract the data
    d = data_voxelize["d"]
    c = data_voxelize["c"]
    size = data_voxelize["size"]
    domain_color = data_voxelize["domain_color"]
    layer_stack = data_voxelize["layer_stack"]

    # voxelize the PNG files
    with utils_log.BlockTimer(LOGGER, "mesher_png"):
        (n, domain_def) = mesher_png.get_mesh(size, domain_color, layer_stack)

    # assemble the data
    data_voxel = {
        "n": n,
        "d": d,
        "c": c,
        "domain_def": domain_def,
    }

    return data_voxel


def _run_stl(data_voxelize):
    """
    Generate a 3D voxel structure from 3D STL files.
    """

    # extract the data
    n = data_voxelize["n"]
    d = data_voxelize["d"]
    c = data_voxelize["c"]
    sampling = data_voxelize["sampling"]
    xyz_min = data_voxelize["xyz_min"]
    xyz_max = data_voxelize["xyz_max"]
    domain_stl = data_voxelize["domain_stl"]

    # voxelize the STL files
    with utils_log.BlockTimer(LOGGER, "mesher_stl"):
        (n, d, c, domain_def, reference) = mesher_stl.get_mesh(n, d, c, sampling, xyz_min, xyz_max, domain_stl)

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
    resampling = data_mesher["resampling"]
    domain_connection = data_mesher["domain_connection"]
    domain_conflict = data_mesher["domain_conflict"]

    # extract the data
    n = data_voxel["n"]
    d = data_voxel["d"]
    c = data_voxel["c"]
    domain_def = data_voxel["domain_def"]

    with utils_log.BlockTimer(LOGGER, "voxel_conflict"):
        domain_def = voxel_conflict.get_conflict(domain_def, domain_conflict)

    with utils_log.BlockTimer(LOGGER, "voxel_resample"):
        (n, d, domain_def) = voxel_resample.get_remesh(n, d, domain_def, resampling)

    with utils_log.BlockTimer(LOGGER, "voxel_connection"):
        connection_def = voxel_connection.get_connection(n, domain_def, domain_connection)

    with utils_log.BlockTimer(LOGGER, "voxel_summary"):
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


def run(data_geometry, path_ref):
    """
    Main script for meshing the geometry and generating a 3D voxel structure.
    Handle invalid data with exceptions.

    Parameters
    ----------
    data_geometry : dict
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

    # get timestamp
    timestamp = utils_log.get_timer()

    # run the code
    try:
        # check the input data
        LOGGER.info("check the input data")
        check_data_geometry.check_data_geometry(data_geometry)
        data_mesher = check_data_mesher.get_data_mesher(data_geometry, path_ref)

        # run the mesher
        (reference, data_voxel) = _run_mesher(data_mesher)

        # resample and assemble
        data_voxel = _run_resample_graph(reference, data_voxel, data_mesher)
    except (CheckError, RunError) as ex:
        utils_log.log_exception(LOGGER, ex)
        return False, None, ex

    # end message
    duration = utils_log.get_duration(timestamp)
    LOGGER.info("duration: %s" % duration)
    LOGGER.info("successful termination")

    return True, data_voxel, None
