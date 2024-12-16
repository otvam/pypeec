"""
Module for parsing voxel indices.
Transform the voxel indices into NumPy arrays.
Check the validity of the indices.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import scilogger
import numpy as np

# get a logger
LOGGER = scilogger.get_logger(__name__, "pypeec")


def get_mesh(param, domain_index):
    """
    Check the domain definition (mapping between domain names and indices).
    """

    # extract the data
    n = param["n"]
    d = param["d"]
    c = param["c"]

    # get total size
    nv = np.prod(n)

    # no reference geometry, direct voxelization
    reference = None

    # init new domain indices
    domain_def = {}

    # check data
    for tag, idx in domain_index.items():
        # disp
        LOGGER.debug("%s: size = %d" % (tag, len(idx)))

        # parse the array
        idx_tmp = np.array(idx, dtype=np.int64)

        # check the indices
        if not (len(np.unique(idx_tmp)) == len(idx_tmp)):
            raise RuntimeError("invalid index: %s: indices should be unique" % tag)
        if not (np.all(idx_tmp >= 0) and np.all(idx_tmp < nv)):
            raise RuntimeError("invalid index: %s: invalid index range" % tag)

        # add the new item
        domain_def[tag] = idx_tmp

    return n, d, c, domain_def, reference
