"""
Module for checking the voxel data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np
from PyPEEC.lib_utils.error import CheckError


def _check_domain_def(n, domain_def):
    """
    Check the domain definition (mapping between domain names and indices).
    """

    # extract the voxel data
    (nx, ny, nz) = n
    n = nx * ny * nz

    # init the domain indices
    idx_domain = np.array([], dtype=np.int64)

    # check type
    if not isinstance(domain_def, dict):
        raise CheckError("domain_def: domain definition should be a dict")

    # check the different domains
    for tag, idx in domain_def.items():
        # check tag
        if not isinstance(tag, str):
            raise CheckError("tag: conductor name should be a string")

        # cast indices
        idx = np.array(idx)
        if not (len(idx.shape) == 1):
            raise CheckError("idx: indices should be a vector")
        if not np.issubdtype(idx.dtype, np.integer):
            raise CheckError("idx: indices should be composed of integers")

        # check for indices range
        if not (np.all(idx >= 0) and np.all(idx < n)):
            raise CheckError("idx: conductor indices should belong to the voxel structure")

        # append
        idx_domain = np.append(idx_domain, idx)

    # check for duplicates
    if not (len(np.unique(idx_domain)) == len(idx_domain)):
        raise CheckError("domain indices should be unique")


def _check_voxel_size(n, d):
    """
    Check the voxel number and dimension.
    """

    # check size
    if not (len(n) == 3):
        raise CheckError("n: invalid voxel number (should be a list with three elements)")
    if not (len(d) == 3):
        raise CheckError("d: invalid voxel size (should be a list with three elements)")

    # check type
    if not all(np.issubdtype(type(x), np.integer) for x in n):
        raise CheckError("n: number of voxels should be composed of integers")
    if not all(np.issubdtype(type(x), np.floating) for x in d):
        raise CheckError("d: dimension of the voxels should be composed of real floats")

    # check value
    if not all((x >= 1) for x in n):
        raise CheckError("n: number of voxels cannot be smaller than one")
    if not all((x > 0) for x in d):
        raise CheckError("d: dimension of the voxels should be positive")


def check_data_voxel(data_voxel):
    """
    Check the voxel structure (number and dimension).
    Check the domain definition (mapping between domain names and indices).
    """

    # check type
    if not isinstance(data_voxel, dict):
        raise CheckError("data_voxel: voxel description should be a dict")

    # extract field
    n = data_voxel["n"]
    d = data_voxel["d"]
    domain_def = data_voxel["domain_def"]

    # check data
    _check_voxel_size(n, d)
    _check_domain_def(n, domain_def)
