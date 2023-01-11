"""
Main script for solving a problem with the FFT-PEEC solver.
Check the input data, solve the problem, and parse the results.

The solver is implemented with NumPy and Scipy.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

from PyPEEC.lib_mesher import check_data
from PyPEEC.lib_shared import logging_utils

# get a logger
logger = logging_utils.get_logger("mesher")


def _run_check(mesh_type, data_mesher):
    """
    Check and combine the input data.
    Exceptions are not caught inside this function.
    The different parts of the code are timed.
    """

    with logging_utils.BlockTimer(logger, "check_data"):
        # check the mesher type
        check_data.check_mesher_type(mesh_type)

        # run the solver
        if mesh_type == "png":
            check_data.check_data_mesher_png(data_mesher)
        elif mesh_type == "stl":
            check_data.check_data_mesher_stl(data_mesher)
        else:
            raise ValueError("invalid mesh type")


def _run_png(data_mesher):
    """
    Compute the voxel geometry, Green functions, and the incidence matrix.
    The different parts of the code are timed.
    """

    # get the voxel geometry and the incidence matrix
    with logging_utils.BlockTimer(logger, "voxel_geometry"):
        pass

    return None


def _run_stl(data_mesher):
    """
    Compute the voxel geometry, Green functions, and the incidence matrix.
    The different parts of the code are timed.
    """

    # get the voxel geometry and the incidence matrix
    with logging_utils.BlockTimer(logger, "voxel_geometry"):
        pass

    return None


def _run_disp(data_voxel):
    """
    Assemble the output data from the different dict.
    """

    pass


def run(mesh_type, data_mesher):
    """
    Main script for solving a problem with the FFT-PEEC solver.
    Handle invalid data with exceptions.
    """

    # init
    logger.info("init")

    # check the input data
    try:
        _run_check(mesh_type, data_mesher)
    except check_data.CheckError as ex:
        logger.error(str(ex))
        return False, None

    # run the solver
    if mesh_type=="png":
        data_voxel = _run_png(data_mesher)
    elif mesh_type=="stl":
        data_voxel = _run_stl(data_mesher)
    else:
        raise ValueError("invalid mesh type")

    # display the results
    _run_disp(data_voxel)

    # end message
    logger.info("successful termination")

    return True, data_voxel
