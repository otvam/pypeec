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


def _get_load_terminal(source, winding_description):
    """
    Get the terminal currents and voltages for a specific sweep.
    """

    # init list
    V_vec = []
    I_vec = []

    # get the solution
    for winding_description_tmp in winding_description:
        # extract the terminal name
        src = winding_description_tmp["src"]
        sink = winding_description_tmp["sink"]

        # extract the terminal quantities
        (V, I) = _get_value_terminal(source, src, sink)

        # add the quantities
        V_vec.append(V)
        I_vec.append(I)

    # assign the data
    V_vec = np.array(V_vec, dtype=np.complex_)
    I_vec = np.array(I_vec, dtype=np.complex_)

    return V_vec, I_vec


def get_extract(data_solution, sweep_name, winding_description, tol_freq):
    """
    Get the terminal currents and voltages for given sweep and windings.
    """

    # extract the data
    data_init = data_solution["data_init"]
    data_sweep = data_solution["data_sweep"]
    status = data_solution["status"]

    # check status
    assert status, "invalid solution"
    assert isinstance(data_init, dict), "invalid solution"
    assert isinstance(data_init, dict), "invalid solution"

    # init data
    V_mat = []
    I_mat = []
    freq_vec = []
    has_converged_vec = []

    # extract data
    for sweep_name_tmp in sweep_name:
        # extract the data
        data_sweep_tmp = data_sweep[sweep_name_tmp]
        freq = data_sweep_tmp["freq"]
        source = data_sweep_tmp["source"]
        has_converged = data_sweep_tmp["has_converged"]

        # compute
        (V_vec, I_vec) = _get_load_terminal(source, winding_description)

        # assign
        V_mat.append(V_vec)
        I_mat.append(I_vec)
        freq_vec.append(freq)
        has_converged_vec.append(has_converged)

    # assemble convergence
    has_converged = np.all(has_converged_vec)
    has_converged = has_converged.item()

    # assemble frequency
    freq = np.mean(freq_vec)
    freq = freq.item()

    # check frequency
    assert np.ptp(freq_vec) < tol_freq, "invalid solution: invalid frequency"
    assert np.all(has_converged_vec), "invalid solution: convergence issue"

    # compute the frequency
    freq = np.mean(freq_vec)

    # create data
    terminal = {
        "n_solution": len(sweep_name),
        "n_winding": len(winding_description),
        "V_mat": np.array(V_mat, dtype=np.complex_).transpose(),
        "I_mat": np.array(I_mat, dtype=np.complex_).transpose(),
        "freq": freq,
    }

    return terminal
