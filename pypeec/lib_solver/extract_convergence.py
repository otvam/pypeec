"""
Provide a function to extract convergence metrics from the solution vector.

The complex power is extracted at the different terminals.
The total complex power is computed for all the terminals.
The active and reactive power are returned as metrics.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import numpy as np
from pypeec import config

# get config
NP_TYPES = config.NP_TYPES


def _get_sol_extract(sol, sol_idx):
    """
    Extract the different variables from the solution vector.
    """

    V_vc = sol[sol_idx["V_vc"]]
    I_fc = sol[sol_idx["I_fc"]]
    I_src = sol[sol_idx["I_src"]]

    return V_vc, I_fc, I_src


def _get_total_power(freq, source_pos, I_src, V_vc):
    """
    Compute the total complex power is computed for all the terminals.
    """

    # get the factor for getting the power time-averaged values
    if freq == 0:
        fact = 1.0
    else:
        fact = 0.5

    # init terminal power
    power = 0.0

    # parse the source terminals
    for tag, source_pos_tmp in source_pos.items():
        # extract the data
        idx_vc = source_pos_tmp["idx_vc"]
        idx_src = source_pos_tmp["idx_src"]

        # get the current and voltage
        if (len(idx_vc) != 0) and (len(idx_src) != 0):
            V_tmp = NP_TYPES.COMPLEX(V_vc[idx_vc])
            I_tmp = NP_TYPES.COMPLEX(I_src[idx_src])

            # compute the apparent power
            power_tmp = np.sum(fact*V_tmp*np.conj(I_tmp))

            # add the power
            power += power_tmp

    return power


def _get_conv_eval(sol, freq, source_pos, sol_idx):
    """
    Extract the convergence metrics (active and reactive power) from a solution vector.
    """

    # extract the data
    (V_vc, I_fc, I_src) = _get_sol_extract(sol, sol_idx)

    # get the sources
    power = _get_total_power(freq, source_pos, I_src, V_vc)

    return power


def get_fct_conv(freq, source_pos, sol_idx):
    """
    Return a function that extract convergence metrics from the solution vector.
    """

    def fct_conv(sol):
        power = _get_conv_eval(sol, freq, source_pos, sol_idx)
        return power

    return fct_conv
