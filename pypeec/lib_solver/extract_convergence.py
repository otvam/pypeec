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
    I_fm = sol[sol_idx["I_fm"]]
    I_src = sol[sol_idx["I_src"]]

    return V_vc, I_fc, I_fm, I_src


def _get_losses(freq, I_fc, I_fm, R_c, R_m):
    """
    Get the losses for the electric and magnetic domains.
    """

    # get the angular frequency
    s = 1j*2*np.pi*freq

    # get the factor for getting the loss time-averaged values
    if freq == 0:
        fact = 1.0
    else:
        fact = 0.5

    # get the magnetic losses linked with the electric domains
    P_fc = fact*np.conj(I_fc)*R_c*I_fc
    P_fc = np.real(P_fc)
    P_fc = np.sum(P_fc)

    # get the magnetic losses linked with the magnetic domains
    P_fm = fact*np.conj(s*I_fm)*R_m*I_fm
    P_fm = np.real(P_fm)
    P_fm = np.sum(P_fm)

    # assign losses
    losses = {"electric": P_fc, "magnetic": P_fm}

    return losses


def _get_source(freq, source_pos, I_src, V_vc):
    """
    Parse the terminal voltages and currents for the sources.
    The sources have internal resistances/admittances.
    Therefore, the extracted value can differ from the source value.
    The results are assigned to a dict with the voltage and current values.
    """

    # init source dict
    source = {}

    # get the factor for getting the power time-averaged values
    if freq == 0:
        fact = 1.0
    else:
        fact = 0.5

    # parse the source terminals
    for tag, source_pos_tmp in source_pos.items():
        # extract the data
        idx_vc = source_pos_tmp["idx_vc"]
        idx_src = source_pos_tmp["idx_src"]

        # voltage is the average between all the voxels composing the terminal
        if len(idx_vc) == 0:
            V_tmp = NP_TYPES.COMPLEX(0)
        else:
            V_tmp = NP_TYPES.COMPLEX(np.mean(V_vc[idx_vc]))

        # current is the sum between all the voxels composing the terminal
        if len(idx_src) == 0:
            I_tmp = NP_TYPES.COMPLEX(0)
        else:
            I_tmp = NP_TYPES.COMPLEX(np.sum(I_src[idx_src]))

        # compute the apparent power
        S_tmp = fact*V_tmp*np.conj(I_tmp)

        # assign the current and voltage
        source[tag] = S_tmp

    return source


def _get_conv_eval(sol, freq, source_idx, sol_idx, idx_vc, idx_src_c, idx_src, R_c, R_m):
    pass



def get_fct_conv(freq, source_pos, sol_idx, R_c, R_m):



    def fct_conv(sol):
        # extract the data
        (V_vc, I_fc, I_fm, I_src) = _get_sol_extract(sol, sol_idx)

        # get the losses
        losses = _get_losses(freq, I_fc, I_fm, R_c, R_m)

        # get the sources
        source = _get_source(freq, source_pos, I_src, V_vc)

        return losses, source






    return fct_conv