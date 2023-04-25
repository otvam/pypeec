"""
Module for extracting the terminal currents and voltage from a solution.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import numpy as np


def _get_value_terminal(source, src, sink):
    """
    Get the terminal values (current and voltage).
    """

    V = source[src]["V"]-source[sink]["V"]
    I = (source[src]["I"]-source[sink]["I"])/2
    S = (source[src]["S"]-source[sink]["S"])/2

    return V, I, S


def _get_load_terminal(freq, source, has_converged, winding_description):
    """
    Get the terminal currents and voltages for a specific sweep.
    """

    # init list
    V_vec = []
    I_vec = []
    S_vec = []

    # get the solution
    for winding_description_tmp in winding_description:
        # extract the terminal name
        src = winding_description_tmp["src"]
        sink = winding_description_tmp["sink"]

        # extract the terminal quantities
        (V, I, S) = _get_value_terminal(source, src, sink)

        # add the quantities
        V_vec.append(V)
        I_vec.append(I)
        S_vec.append(S)

    # assign the data
    V_vec = np.array(V_vec, dtype=np.complex_)
    I_vec = np.array(I_vec, dtype=np.complex_)
    S_vec = np.array(S_vec, dtype=np.complex_)

    # assign
    terminal = {
        "freq": freq, "has_converged": has_converged,
        "V_vec": V_vec, "I_vec": I_vec, "S_vec": S_vec,
    }

    return terminal


def get_extract(data_solution, winding_description, sweep_list):
    """
    Get the terminal currents and voltages for all the sweeps.
    """

    # extract the data
    data_init = data_solution["data_init"]
    data_sweep = data_solution["data_sweep"]

    # check solution
    assert isinstance(data_init, dict), "invalid solution"
    assert isinstance(data_sweep, dict), "invalid solution"

    # matrix size
    n_winding = len(winding_description)

    # extract data
    terminal = {}
    for tag in sweep_list:
        # extract the data
        data_sweep_tmp = data_sweep[tag]
        freq = data_sweep_tmp["freq"]
        source = data_sweep_tmp["source"]
        has_converged = data_sweep_tmp["has_converged"]

        # assign
        terminal[tag] = _get_load_terminal(freq, source, has_converged, winding_description)

    return n_winding, terminal
