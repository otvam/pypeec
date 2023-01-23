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
__copyright__ = "(c) 2023 - Dartmouth College"

from PyPEEC.lib_mesher import png_mesher
from PyPEEC.lib_mesher import stl_mesher
from PyPEEC.lib_mesher import voxel_resample
from PyPEEC.lib_mesher import voxel_graph
from PyPEEC.lib_mesher import voxel_summary
from PyPEEC.lib_check import check_data_mesher
from PyPEEC.lib_utils import timelogger
from PyPEEC.lib_utils.error import CheckError, RunError

# get a logger
logger = timelogger.get_logger("MESHER")


def _run_check(data_mesher):
    """
    Check and combine the input data.
    Exceptions are not caught inside this function.
    """

    with timelogger.BlockTimer(logger, "check_data"):
        # check the mesher data
        (mesh_type, data_voxelize, n_resampling) = check_data_mesher.check_data_mesher(data_mesher)

        # check the mesher type
        check_data_mesher.check_mesh_type(mesh_type)

        # check the resampling data
        check_data_mesher.check_n_resampling(n_resampling)

        # check the mesher
        if mesh_type == "png":
            check_data_mesher.check_data_voxelize_png(data_voxelize)
        elif mesh_type == "stl":
            check_data_mesher.check_data_voxelize_stl(data_voxelize)
        elif mesh_type == "voxel":
            check_data_mesher.check_data_voxelize_voxel(data_voxelize)
        else:
            raise CheckError("invalid mesh type")

        return mesh_type, data_voxelize, n_resampling


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
    pts_min = data_voxelize["pts_min"]
    pts_max = data_voxelize["pts_max"]
    domain_stl = data_voxelize["domain_stl"]
    domain_conflict = data_voxelize["domain_conflict"]

    # get the voxel geometry and the incidence matrix
    with timelogger.BlockTimer(logger, "voxel_geometry"):
        domain_stl = check_data_mesher.get_domain_stl_path(domain_stl, path_ref)
        (d, c, domain_def) = stl_mesher.get_mesh(n, pts_min, pts_max, domain_stl)
        domain_def = stl_mesher.get_conflict(domain_def, domain_conflict)

    # assemble the data
    data_voxel = {
        "n": n,
        "d": d,
        "c": c,
        "domain_def": domain_def,
    }

    return data_voxel


def _run_resample_graph(data_voxel, n_resampling):
    """
    Resampling of a 3D voxel structure (increases the number of voxels).
    """

    # extract the data
    n = data_voxel["n"]
    d = data_voxel["d"]
    c = data_voxel["c"]
    domain_def = data_voxel["domain_def"]

    with timelogger.BlockTimer(logger, "voxel_resample"):
        (n, d, domain_def) = voxel_resample.get_remesh(n, d, domain_def, n_resampling)

    with timelogger.BlockTimer(logger, "voxel_graph"):
        graph_def = voxel_graph.get_graph(n, domain_def)

    with timelogger.BlockTimer(logger, "voxel_summary"):
        voxel_status = voxel_summary.get_status(n, d, c, domain_def, graph_def)

    # assemble the data
    data_voxel = {
        "n": n,
        "d": d,
        "c": c,
        "domain_def": domain_def,
        "graph_def": graph_def,
        "voxel_status": voxel_status,
    }

    return data_voxel


def run(data_mesher, path_ref):
    """
    Main script for meshing the geometry and generating a 3D voxel structure.
    Handle invalid data with exceptions.

    Parameters
    ----------
    data_mesher : dict
        This file is an input file (JSON format).
        The dict describes the meshing and resampling process.
        The voxel structure can be explicitly given or generated from PNG or STL files.
    path_ref :  path (string)
        Path used to load the PNG and STL files.
        Typically, this will be the path of the containing the mesher data.

    Returns
    -------
    status : boolean
        True if the call is successful.
        False if the problems are encountered
    data_voxel: dict
        The dict describes the voxel structure.
        The voxel grid (number, size, and origin) is defined.
        Different domains (with the indices of the voxel) are defined.
        The connected components of the graph defined by the voxel structure are defined.
    """

    # run the code
    try:
        # check the input data
        (mesh_type, data_voxelize, n_resampling) = _run_check(data_mesher)

        # run the mesher
        if mesh_type == "png":
            data_voxel = _run_png(data_voxelize, path_ref)
        elif mesh_type == "stl":
            data_voxel = _run_stl(data_voxelize, path_ref)
        elif mesh_type == "voxel":
            data_voxel = data_voxelize
        else:
            raise CheckError("invalid mesh type")

        # resample and assemble
        data_voxel = _run_resample_graph(data_voxel, n_resampling)
    except CheckError as ex:
        logger.error("check error : " + str(ex))
        return False, None
    except RunError as ex:
        logger.error("check error : " + str(ex))
        return False, None

    # end message
    logger.info("successful termination")

    return True, data_voxel
