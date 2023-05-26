"""
Different functions for extracting the fields and terminal currents and voltages from the solution vector.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import numpy as np
from pypeec import config

# get config
NP_TYPES = config.NP_TYPES


def _get_sol_extract(sol, sol_idx):
    """
    Extract the electric/magnetic variables from the solution vector.
    """

    V_vc = sol[sol_idx["V_vc"]]
    I_fc = sol[sol_idx["I_fc"]]
    I_src = sol[sol_idx["I_src"]]

    return V_vc, I_fc, I_src


def _get_total_power(freq, source_pos, I_src, V_vc):
    """
    Parse the terminal voltages and currents for the sources.
    The sources have internal resistances/admittances.
    Therefore, the extracted value can differ from the source value.
    The results are assigned to a dict with the voltage and current values.
    """

    # get the factor for getting the power time-averaged values
    if freq == 0:
        fact = 1.0
    else:
        fact = 0.5

    # init terminal power
    S_tot = 0.0

    # parse the source terminals
    for tag, source_pos_tmp in source_pos.items():
        # extract the data
        idx_vc = source_pos_tmp["idx_vc"]
        idx_src = source_pos_tmp["idx_src"]

        # get the current and voltage
        if (len(idx_vc) != 0) and (len(idx_src) != 0):
            V_tmp = NP_TYPES.COMPLEX(np.mean(V_vc[idx_vc]))
            I_tmp = NP_TYPES.COMPLEX(np.sum(I_src[idx_src]))

            # compute the apparent power
            S_tmp = fact*V_tmp*np.conj(I_tmp)

            # add the power
            S_tot += S_tmp

    return S_tot


def _get_conv_eval(sol, freq, source_pos, sol_idx):
    # extract the data
    (V_vc, I_fc, I_src) = _get_sol_extract(sol, sol_idx)

    # get the sources
    S_tot = _get_total_power(freq, source_pos, I_src, V_vc)

    # extract the data
    P_tot = np.real(S_tot)
    Q_tot = np.imag(S_tot)

    return P_tot, Q_tot


def get_fct_conv(freq, source_pos, sol_idx):
    def fct_conv(sol):
        source = _get_conv_eval(sol, freq, source_pos, sol_idx)
        return source

    return fct_conv