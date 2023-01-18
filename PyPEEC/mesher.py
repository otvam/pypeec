"""
Main script for creating a voxel structure.
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
from PyPEEC.lib_check import check_data_mesher
from PyPEEC.lib_utils import timelogger
from PyPEEC.lib_utils.error import CheckError, RunError

# get a logger
logger = timelogger.get_logger("mesher")


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

    # assemble the data
    data_voxel = {
        "n": n,
        "d": d,
        "c": c,
        "domain_def": domain_def,
        "graph_def": graph_def,
    }

    return data_voxel


def _run_disp(data_voxel):
    """
    Display the voxel structure statistics (number and size).
    """

    # extract the data
    n = data_voxel["n"]
    d = data_voxel["d"]
    c = data_voxel["c"]
    domain_def = data_voxel["domain_def"]
    graph_def = data_voxel["graph_def"]

    # extract the voxel data
    (nx, ny, nz) = n
    (dx, dy, dz) = d
    (cx, cy, cz) = c

    # compute
    n_voxel = nx*ny*nz
    n_graph = len(graph_def)

    # plot the voxel size
    logger.info("(nx, ny, nz)) = (%d, %d, %d)" % (nx, ny, nz))
    logger.info("(dx, dy, dz) =  (%.3e, %.3e, %.3e)" % (dx, dy, dz))
    logger.info("(cx, cy, cz) =  (%.3e, %.3e, %.3e)" % (cx, cy, cz))
    logger.info("n_voxel = %d" % n_voxel)
    logger.info("n_graph = %d" % n_graph)

    # plot the domain size
    for tag, idx in domain_def.items():
        logger.info("domain / %s = %d" % (tag, len(idx)))


def run(data_mesher, path_ref):
    """
    Main script for creating a voxel structure.
    Handle invalid data with exceptions.
    """

    # init
    logger.info("init")

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

        # display the results
        _run_disp(data_voxel)
    except CheckError as ex:
        logger.error("check error : " + str(ex))
        return False, None
    except RunError as ex:
        logger.error("check error : " + str(ex))
        return False, None

    # end message
    logger.info("successful termination")

    return True, data_voxel
