"""
Main script for solving a problem with the FFT-PEEC solver.
Check the input data, solve the problem, and parse the results.

The solver is implemented with NumPy and Scipy.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

from PyPEEC.lib_mesher import png_mesher
from PyPEEC.lib_mesher import stl_mesher
from PyPEEC.lib_mesher import voxel_resample
from PyPEEC.lib_shared import logging_utils
from PyPEEC.lib_shared import check_data_mesher
from PyPEEC.lib_shared import check_data_voxel
from PyPEEC.lib_shared.check_data_error import CheckError

# get a logger
logger = logging_utils.get_logger("mesher")


def _run_check(mesh_type, data_mesher, data_resampling):
    """
    Check and combine the input data.
    Exceptions are not caught inside this function.
    The different parts of the code are timed.
    """

    with logging_utils.BlockTimer(logger, "check_data"):
        # check the mesher type
        check_data_mesher.check_mesher_type(mesh_type)

        # check the mesher
        if mesh_type == "png":
            check_data_mesher.check_data_mesher_png(data_mesher)
        elif mesh_type == "stl":
            check_data_mesher.check_data_mesher_stl(data_mesher)
        elif mesh_type == "voxel":
            pass
        else:
            raise ValueError("invalid mesh type")

        # check the resampling data
        check_data_mesher.check_data_resampling(data_resampling)


def _run_png(data_mesher):
    """
    Compute the voxel geometry, Green functions, and the incidence matrix.
    The different parts of the code are timed.
    """

    # extract the data
    d = data_mesher["d"]
    nx = data_mesher["nx"]
    ny = data_mesher["ny"]
    domain_color = data_mesher["domain_color"]
    layer_stack = data_mesher["layer_stack"]

    # get the voxel geometry and the incidence matrix
    with logging_utils.BlockTimer(logger, "png_mesher"):
        (n, domain_def) = png_mesher.get_mesh(nx, ny, domain_color, layer_stack)

    # assemble the data
    data_voxel = {
        "n": n,
        "d": d,
        "domain_def": domain_def,
    }

    return data_voxel


def _run_stl(data_mesher):
    """
    Compute the voxel geometry, Green functions, and the incidence matrix.
    The different parts of the code are timed.
    """

    # extract the data
    n = data_mesher["n"]
    pts_min = data_mesher["pts_min"]
    pts_max = data_mesher["pts_max"]
    domain_stl = data_mesher["domain_stl"]
    domain_conflict = data_mesher["domain_conflict"]

    # get the voxel geometry and the incidence matrix
    with logging_utils.BlockTimer(logger, "voxel_geometry"):
        (d, domain_def) = stl_mesher.get_mesh(n, pts_min, pts_max, domain_stl)
        domain_def = stl_mesher.get_conflict(domain_def, domain_conflict)

    # assemble the data
    data_voxel = {
        "n": n,
        "d": d,
        "domain_def": domain_def,
    }

    return data_voxel


def _run_resample(data_voxel, data_resampling):
    # extract the data
    n = data_voxel["n"]
    d = data_voxel["d"]
    domain_def = data_voxel["domain_def"]
    use_resampling = data_resampling["use_resampling"]
    n_resampling = data_resampling["n_resampling"]

    if use_resampling:
        with logging_utils.BlockTimer(logger, "voxel_resample"):
            (n, d, domain_def) = voxel_resample.get_remesh(n, d, domain_def, n_resampling)

    # assemble the data
    data_voxel = {
        "n": n,
        "d": d,
        "domain_def": domain_def,
    }

    return data_voxel


def _run_disp(data_voxel):
    """
    Assemble the output data from the different dict.
    """

    # extract the data
    n = data_voxel["n"]
    d = data_voxel["d"]
    domain_def = data_voxel["domain_def"]

    # extract the voxel data
    (nx, ny, nz) = n
    (dx, dy, dz) = d
    n = nx*ny*nz

    # plot the voxel size
    logger.info("(nx, ny, nz)) = (%d, %d, %d)" % (nx, ny, nz))
    logger.info("(dx, dy, dz) =  (%.3e, %.3e, %.3e)" % (dx, dy, dz))
    logger.info("n = %d" % n)

    # plot the domain size
    for tag, idx in domain_def.items():
        logger.info("domain / %s = %d" % (tag, len(idx)))


def run(mesh_type, data_mesher, data_resampling):
    """
    Main script for solving a problem with the FFT-PEEC solver.
    Handle invalid data with exceptions.
    """

    # init
    logger.info("init")

    # run the code
    try:
        # check the input data
        _run_check(mesh_type, data_mesher, data_resampling)

        # run the mesher
        if mesh_type == "png":
            data_voxel = _run_png(data_mesher)
        elif mesh_type == "stl":
            data_voxel = _run_stl(data_mesher)
        elif mesh_type == "voxel":
            data_voxel = data_mesher
        else:
            raise ValueError("invalid mesh type")

        # resample and assemble
        data_voxel = _run_resample(data_voxel, data_resampling)

        # display the results
        _run_disp(data_voxel)

        # check the output
        check_data_voxel.check_data_voxel(data_voxel)
    except CheckError as ex:
        logger.error(str(ex))
        return False, None

    # end message
    logger.info("successful termination")

    return True, data_voxel
