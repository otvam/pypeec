"""
Convert voxel indices (linear and tensor indices).
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

# base packages
import scilogger

# import utils to be demonstrated
from pypeec.utils import voxel

# get a logger
LOGGER = scilogger.get_logger(__name__, "script")


if __name__ == "__main__":
    # ########################################################
    # ### definition of the parameters
    # ########################################################

    # size of the voxel structure
    n = [5, 5, 7]

    # dictionary with the voxel indices
    idx_input = {
        "src": [],
        "sink": [],
        "wire": [],
        "core": [],
    }

    # position of the wire and terminals
    idx_x = 2
    idx_y = 2
    idx_z_min = 0
    idx_z_max = 6

    # definition of terminal indices
    idx_input["src"].append([idx_x, idx_y, idx_z_min])
    idx_input["sink"].append([idx_x, idx_y, idx_z_max])

    # definition of wire indices
    for idx_z in range(idx_z_min + 1, idx_z_max + 0):
        idx_input["wire"].append([idx_x, idx_y, idx_z])

    # position of the magnetic core
    idx_xy_min = 0
    idx_xy_max = 4
    idx_z_min = 2
    idx_z_max = 4

    # definition of core indices
    for idx_z in range(idx_z_min + 0, idx_z_max + 1):
        for idx_x in range(idx_xy_min + 0, idx_xy_max + 1):
            for idx_y in range(idx_xy_min + 0, idx_xy_max + 1):
                if (idx_x in [idx_xy_min, idx_xy_max]) or (idx_y in [idx_xy_min, idx_xy_max]):
                    idx_input["core"].append([idx_x, idx_y, idx_z])

    # ########################################################
    # ### convert the indices
    # ########################################################

    # convert tensor to linear indices
    LOGGER.info("convert tensor to linear indices")
    idx_linear = {tag: voxel.get_idx_linear(n, idx) for tag, idx in idx_input.items()}

    # convert linear to tensor indices
    LOGGER.info("convert linear to tensor indices")
    idx_tensor = {tag: voxel.get_idx_tensor(n, idx) for tag, idx in idx_linear.items()}

    # ########################################################
    # ### display the results
    # ########################################################

    # display the linear indices
    LOGGER.info("show the linear indices")
    with LOGGER.BlockIndent():
        for tag, idx in idx_linear.items():
            LOGGER.info("%s = %s" % (tag, idx.tolist()))

    # display the tensor indices
    LOGGER.info("shoow the tensor indices")
    with LOGGER.BlockIndent():
        for tag, idx in idx_tensor.items():
            LOGGER.info("%s = %s" % (tag, idx.tolist()))
