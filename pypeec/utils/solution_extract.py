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

    # get length
    n_winding = len(winding_description)

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

    return n_winding, terminal


def get_extract(data_solution, sweep_description):
    """
    Get the terminal currents and voltages for given sweep and windings.
    The winding description can be different for the sweeps.
    """

    # extract the data
    data_init = data_solution["data_init"]
    data_sweep = data_solution["data_sweep"]
    status = data_solution["status"]

    # check status
    assert status, "invalid solution"
    assert isinstance(data_init, dict), "invalid solution"
    assert isinstance(data_init, dict), "invalid solution"

    # extract data
    terminal = []
    n_winding = []
    for sweep_description_tmp in sweep_description:
        # extract data
        sweep_name = sweep_description_tmp["sweep_name"]
        winding_description = sweep_description_tmp["winding_description"]

        # extract the data
        data_sweep_tmp = data_sweep[sweep_name]
        freq = data_sweep_tmp["freq"]
        source = data_sweep_tmp["source"]
        has_converged = data_sweep_tmp["has_converged"]

        # compute
        (n_winding_tmp, terminal_tmp) = _get_load_terminal(freq, source, has_converged, winding_description)

        # assign
        terminal.append(terminal_tmp)
        n_winding.append(n_winding_tmp)

    # check winding length
    n_winding = np.unique(n_winding)
    assert len(n_winding) == 1, "invalid winding number"

    # cast to scalar
    n_winding = n_winding.item()

    return n_winding, terminal


def get_extract_complete(data_solution, sweep_name_list, winding_description):
    """
    Get the terminal currents and voltages for given sweep and windings.
    The winding description is the same for all the sweeps.
    """

    # create the sweep and winding description
    sweep_description = []
    for sweep_name in sweep_name_list:
        sweep_description.append({"sweep_name": sweep_name, "winding_description": winding_description})

    # extract the data
    (n_winding, terminal) = get_extract(data_solution, sweep_description)

    return n_winding, terminal


def get_extract_symmetric(data_solution, sweep_name, winding_description):
    """
    Get the terminal currents and voltages for a simulation with symmetric windings.
    A single sweep is used and the winding description circularly shifted.
    """

    # create the sweep and winding description
    sweep_description = []
    for i in range(len(winding_description)):
        winding_description_shift = np.roll(winding_description, i).tolist()
        sweep_description.append({"sweep_name": sweep_name, "winding_description": winding_description_shift})

    # extract the data
    (n_winding, terminal) = get_extract(data_solution, sweep_description)

    return n_winding, terminal
