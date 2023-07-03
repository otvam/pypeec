"""
Different functions for resolving conflict between domains.
Detect and remove shared indices (conflict) between domains.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import numpy as np
from pypeec import config
from pypeec.error import RunError

# get config
NP_TYPES = config.NP_TYPES


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


def _get_resolution(domain_def):
    """
    Check that all the conflicts are resolved.
    """

    # assemble all the indices
    idx_all = np.array([], dtype=NP_TYPES.INT)
    for idx in domain_def.values():
        idx_all = np.append(idx_all, idx)

    # check that all the conflicts are resolved
    if not (len(np.unique(idx_all)) == len(idx_all)):
        raise RunError("invalid domain: domain indices should be unique")


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

    # check that the conflicts are resolved
    _get_resolution(domain_def)

    return domain_def
