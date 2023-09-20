"""
Module for parsing voxel indices.
Transform the voxel indices into NumPy arrays.
Check the validity of the indices.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import numpy as np
from pypeec import log
from pypeec import config
from pypeec.error import RunError

# get a logger
LOGGER = log.get_logger("VOXEL")

# get config
NP_TYPES = config.NP_TYPES

# get problem size limits
VOXEL_TOTAL = config.PROBLEM_MAX_SIZE.VOXEL_TOTAL
VOXEL_USED = config.PROBLEM_MAX_SIZE.VOXEL_USED


def get_mesh(param, domain_index):
    """
    Check the domain definition (mapping between domain names and indices).
    """

    # extract the data
    n = param["n"]
    d = param["d"]
    c = param["c"]

    # no reference geometry, direct voxelization
    reference = None

    # check total size
    nv = np.prod(n)
    if (VOXEL_TOTAL is not None) and (nv > VOXEL_TOTAL):
        raise RunError("invalid size of the voxel structure: %d" % nv)

    # init new domain indices
    domain_def = {}

    # check data
    for tag, idx in domain_index.items():
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
        domain_def[tag] = idx_tmp

    # check used size
    nv = sum(len(idx) for idx in domain_def.values())
    if (VOXEL_USED is not None) and (nv > VOXEL_USED):
        raise RunError("invalid number of used voxels: %d" % nv)

    return n, d, c, domain_def, reference
