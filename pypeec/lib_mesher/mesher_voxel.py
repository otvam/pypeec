"""
Module for parsing voxel indices.
Transform the voxel indices into NumPy arrays.
Check the validity of the indices.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import numpy as np
from pypeec import utils_log
from pypeec import config
from pypeec.error import RunError

# get a logger
LOGGER = utils_log.get_logger("VOXEL")

# get config
NP_TYPES = config.NP_TYPES


def get_mesh(n, domain_def):
    """
    Check the domain definition (mapping between domain names and indices).
    """

    # extract the voxel data
    (nx, ny, nz) = n
    nv = nx*ny*nz

    # init new domain indices
    domain_def_array = {}

    # check data
    for tag, idx in domain_def.items():
        # disp
        LOGGER.debug("%s: size = %d" % (tag, len(idx)))

        # parse the array
        idx_tmp = np.array(idx, dtype=NP_TYPES.INT)

        # check the indices
        if not (len(np.unique(idx_tmp)) == len(idx_tmp)):
            raise RunError("invalid index: %s: indices should be unique" % tag)
        if not (np.all(idx_tmp >= 0) and np.all(idx_tmp < nv)):
            raise RunError("invalid index: %s: invalid index range" % tag)

        # add the new item
        domain_def_array[tag] = idx_tmp

    return domain_def_array
