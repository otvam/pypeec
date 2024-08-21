"""
Different functions for resolving conflict between domains.
Detect and remove shared indices (conflict) between domains.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import numpy as np
import numpy.random as rnd


def _get_solve_overlap(domain_def, domain_resolve, domain_keep):
    """
    Detect and remove shared indices (conflict) between two domains.
    The conflict is solved in the following way:
        - the reference domain remains unchanged
        - the shared indices are removed from the domain to be fixed
    """

    for domain_keep_tmp in domain_keep:
        for domain_resolve_tmp in domain_resolve:
            # get the indices
            idx_keep = domain_def[domain_keep_tmp]
            idx_resolve = domain_def[domain_resolve_tmp]

            # resolve the conflict
            idx_resolve = np.setdiff1d(idx_resolve, idx_keep)

            # update the domain indices
            domain_def[domain_resolve_tmp] = idx_resolve

    return domain_def


def _get_random(domain_def):
    """
    Random assignment of the duplicated voxel indices.
    """

    # assemble all the indices
    idx_tag = np.empty(0, dtype=np.int_)
    idx_vox = np.empty(0, dtype=np.int_)
    for idx_tag_tmp, idx_vox_tmp in enumerate(domain_def.values()):
        idx_tag = np.append(idx_tag, np.repeat(idx_tag_tmp, len(idx_vox_tmp)))
        idx_vox = np.append(idx_vox, idx_vox_tmp)

    # shuffle indices
    idx_tmp = rnd.permutation(len(idx_tag))
    idx_tag = idx_tag[idx_tmp]
    idx_vox = idx_vox[idx_tmp]

    # find the first occurrence for the indices
    (idx_vox, idx_uni) = np.unique(idx_vox, return_index=True)
    idx_tag = idx_tag[idx_uni]

    # assign the unique indices
    for idx_tag_tmp, tag in enumerate(domain_def.keys()):
        domain_def[tag] = idx_vox[idx_tag == idx_tag_tmp]

    return domain_def


def _get_resolution(domain_def):
    """
    Check that all the conflicts are resolved.
    """

    # assemble all the indices
    idx_all = np.empty(0, dtype=np.int_)
    for idx in domain_def.values():
        idx_all = np.append(idx_all, idx)

    # check that all the conflicts are resolved
    if not (len(np.unique(idx_all)) == len(idx_all)):
        raise RuntimeError("invalid domain: domain indices should be unique")


def get_conflict(domain_def, domain_conflict):
    """
    Detect and remove shared indices (conflict) between domains.
    The direction of the conflict resolution (between two domains) is specified by the user.
    At the end, check that all shared indices have been removed.
    """

    # resolve the conflicts for all the specified domain pairs
    for domain_conflict_tmp in domain_conflict:
        # extract the data
        domain_resolve = domain_conflict_tmp["domain_resolve"]
        domain_keep = domain_conflict_tmp["domain_keep"]

        # solve the conflict
        domain_def = _get_solve_overlap(domain_def, domain_resolve, domain_keep)

    # random assignment of the duplicates
    domain_def = _get_random(domain_def)

    # check that the conflicts are resolved
    _get_resolution(domain_def)

    return domain_def
