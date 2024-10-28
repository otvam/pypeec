"""
Different functions for resolving conflict between domains.
Detect and remove shared indices (conflict) between domains.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import numpy as np
import numpy.random as rnd


def _get_solve_overlap(domain_def, conflict_rules):
    """
    Detect and remove shared indices (conflict) between two domains.
    The conflict is solved in the following way:
        - the reference domain remains unchanged
        - the shared indices are removed from the domain to be fixed
    """

    # extract the data
    domain_keep = conflict_rules["domain_keep"]
    domain_resolve = conflict_rules["domain_resolve"]

    # apply the conflict resolution rule
    for domain_keep_tmp in domain_keep:
        for domain_resolve_tmp in domain_resolve:
            # check domain
            if domain_keep_tmp not in domain_def:
                raise RuntimeError("invalid domain: name not found: %s" % domain_keep_tmp)
            if domain_resolve_tmp not in domain_def:
                raise RuntimeError("invalid domain: name not found: %s" % domain_resolve_tmp)

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
    idx_tag = np.empty(0, dtype=np.int64)
    idx_vox = np.empty(0, dtype=np.int64)
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
    idx_all = np.empty(0, dtype=np.int64)
    for idx in domain_def.values():
        idx_all = np.append(idx_all, idx)

    # check that all the conflicts are resolved
    if not (len(np.unique(idx_all)) == len(idx_all)):
        raise RuntimeError("invalid domain: domain indices should be unique")


def get_conflict(domain_def, data_conflict):
    """
    Detect and remove shared indices (conflict) between domains.
    The direction of the conflict resolution (between two domains) is specified by the user.
    After the rule-based resolution, a random resolution can be performed (if desired)
    At the end, the unicity of the voxel indices is checked.
    """

    # extract the data
    resolve_rules = data_conflict["resolve_rules"]
    resolve_random = data_conflict["resolve_random"]
    conflict_rules = data_conflict["conflict_rules"]

    # resolve the conflicts for all the specified domains
    if resolve_rules:
        for conflict_rules_tmp in conflict_rules:
            domain_def = _get_solve_overlap(domain_def, conflict_rules_tmp)

    # random assignment of the duplicates
    if resolve_random:
        domain_def = _get_random(domain_def)

    # check that the conflicts are resolved
    _get_resolution(domain_def)

    return domain_def
