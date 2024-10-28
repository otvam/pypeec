"""
Module for extracting the terminal currents and voltage from a solution.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import numpy as np


def _get_value_terminal(source, src, sink):
    """
    Get the terminal values (current and voltage).
    """

    V = source[src]["V"]-source[sink]["V"]
    I = (source[src]["I"]-source[sink]["I"])/2

    return V, I


def _get_load_terminal(source, terminal_list):
    """
    Get the terminal currents and voltages for a specific sweep.
    """

    # init list
    V_vec = []
    I_vec = []

    # get the solution
    for terminal in terminal_list:
        # extract the terminal name
        src = terminal["src"]
        sink = terminal["sink"]

        # extract the terminal quantities
        (V, I) = _get_value_terminal(source, src, sink)

        # add the quantities
        V_vec.append(V)
        I_vec.append(I)

    # assign the data
    V_vec = np.array(V_vec, dtype=np.complex128)
    I_vec = np.array(I_vec, dtype=np.complex128)

    return V_vec, I_vec


def get_extract(data_solution, sweep_list, terminal_list):
    """
    Get the terminal currents and voltages for given sweeps and windings.
    """

    # extract the data
    data_init = data_solution["data_init"]
    data_sweep = data_solution["data_sweep"]

    # check status
    assert isinstance(data_init, dict), "invalid solution"
    assert isinstance(data_init, dict), "invalid solution"

    # init data
    V_mat = []
    I_mat = []
    freq_vec = []

    # extract data
    for sweep in sweep_list:
        # extract the data
        data_sweep_tmp = data_sweep[sweep]
        freq = data_sweep_tmp["freq"]
        source = data_sweep_tmp["source"]

        # compute
        (V_vec, I_vec) = _get_load_terminal(source, terminal_list)

        # assign
        V_mat.append(V_vec)
        I_mat.append(I_vec)
        freq_vec.append(freq)

    # get and check frequency
    freq = np.mean(freq_vec)
    assert np.allclose(freq_vec, freq), "invalid solution: invalid frequency"

    # create data
    terminal = {
        "n_solution": len(sweep_list),
        "n_winding": len(terminal_list),
        "V_mat": np.array(V_mat, dtype=np.complex128).transpose(),
        "I_mat": np.array(I_mat, dtype=np.complex128).transpose(),
        "freq": freq,
    }

    return terminal
