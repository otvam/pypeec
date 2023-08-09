"""
Module for determining the symmetry between windings.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import numpy as np


def _get_excitation_compact(data, sym):
    # extract
    perm = sym["perm"]
    sim = sym["sim"]

    # cast and check
    perm = np.array(perm, dtype=int)
    if sim >= len(perm):
        raise ValueError("invalid index")

    # combine excitations
    for perm_tmp in perm:
        data[:, perm_tmp] = data[:, perm[sim]]

    return data


def _get_solution_expand(n_winding, data, sym):
    # extract
    perm = sym["perm"]
    sim = sym["sim"]

    # cast and check
    perm = np.array(perm, dtype=int)
    if sim >= len(perm):
        raise ValueError("invalid index")

    # repeat
    data_all = np.zeros((n_winding, 0), dtype=bool)

    # idx
    idx = np.arange(len(perm))

    # combine excitations
    for i in range(len(perm)):
        idx_add = np.roll(idx, i)
        perm_add = perm[idx_add, :]

        data_add = np.copy(data)
        data_add[perm.flatten(), :] = data[perm_add.flatten(), :]

        data_all = np.hstack((data_all, data_add))

    return data_all


def get_excitation_all(n_winding, sym):
    # full excitations
    excitation = np.eye(n_winding, dtype=bool)

    # combine excitations
    for sym_tmp in sym:
        excitation = _get_excitation_compact(excitation, sym_tmp)

    # reduced excitations
    (excitation, idx) = np.unique(excitation, axis=1, return_index=True)

    # get solution
    n_solution = len(idx)

    return n_solution, excitation


def get_solution_all(terminal, sym):
    # extract
    I_mat = terminal["I_mat"]
    V_mat = terminal["V_mat"]
    n_winding = terminal["n_winding"]
    n_solution = terminal["n_solution"]
    freq = terminal["freq"]

    # check size
    assert I_mat.shape == (n_winding, n_solution), "invalid solution: current matrix shape"
    assert V_mat.shape == (n_winding, n_solution), "invalid solution: voltage matrix shape"

    # combine excitations and results
    for sym_tmp in sym:
        I_mat = _get_solution_expand(n_winding, I_mat, sym_tmp)
        V_mat = _get_solution_expand(n_winding, V_mat, sym_tmp)

    # reduced excitations and results
    IV_mat = np.vstack((I_mat, V_mat))
    (_, idx) = np.unique(IV_mat, axis=1, return_index=True)
    I_mat = I_mat[:, idx]
    V_mat = V_mat[:, idx]

    # get solution
    n_solution = len(idx)

    # update terminal
    terminal = {
        "n_winding": n_winding,
        "n_solution": n_solution,
        "freq": freq,
        "I_mat": I_mat,
        "V_mat": V_mat,
    }

    return terminal
