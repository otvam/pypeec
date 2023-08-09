"""
Module for determining and exploiting the symmetry between terminals.

Determine which simulations are required to extract the full impedance matrix.
This means that a reduced set of simulations are performed.
Finally, the full solution is expanded from the reduced set.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import numpy as np


def _get_excitation_compact(data, sym):
    """
    Reduce a matrix with respect to a particular symmetry.
    Only a single excitation per symmetry is kept.
    """

    # extract
    perm = sym["perm"]
    sim = sym["sim"]

    # cast and check
    perm = np.array(perm, dtype=int)
    if sim >= len(perm):
        raise ValueError("invalid index")

    # combine excitations with the symmetry
    for perm_tmp in perm:
        data[:, perm_tmp] = data[:, perm[sim]]

    return data


def _get_solution_expand(n_winding, data, sym):
    """
    Expand a matrix with respect to a particular symmetry.
    Different solutions are generated with permutations.
    The permutations are given by the symmetry.
    """

    # extract
    perm = sym["perm"]
    sim = sym["sim"]

    # cast and check
    perm = np.array(perm, dtype=int)
    if sim >= len(perm):
        raise ValueError("invalid index")

    # initialize the expanded matrix
    data_all = np.zeros((n_winding, 0), dtype=data.dtype)

    # index for the permutation
    idx = np.arange(len(perm))

    # combine excitations
    for i in range(len(perm)):
        # get the permutation to be performed
        idx_add = np.roll(idx, i)
        perm_add = perm[idx_add, :]

        # permute the matrix
        data_add = np.copy(data)
        data_add[perm.flatten(), :] = data[perm_add.flatten(), :]

        # add the permuted matrix the expanded matrix
        data_all = np.hstack((data_all, data_add))

    return data_all


def get_excitation_all(n_winding, sym):
    """
    Determine which simulations are required to extract the full impedance matrix.
    The different symmetries are used to reduce the number of simulations.
    """

    # full excitations
    excitation = np.eye(n_winding, dtype=bool)

    # combine excitations with the symmetries
    for sym_tmp in sym:
        excitation = _get_excitation_compact(excitation, sym_tmp)

    # remove redundant excitations
    (excitation, idx) = np.unique(excitation, axis=1, return_index=True)

    # get the number of solutions for the reduced problem
    n_solution = len(idx)

    return n_solution, excitation


def get_solution_all(terminal, sym):
    """
    Generate a full solution from a reduced solution.
    The different symmetries are used to expand the number of simulations.
    """

    # extract
    I_mat = terminal["I_mat"]
    V_mat = terminal["V_mat"]
    n_winding = terminal["n_winding"]
    n_solution = terminal["n_solution"]
    freq = terminal["freq"]

    # check size
    assert I_mat.shape == (n_winding, n_solution), "invalid solution: current matrix shape"
    assert V_mat.shape == (n_winding, n_solution), "invalid solution: voltage matrix shape"

    # expand the solution with the symmetries
    for sym_tmp in sym:
        I_mat = _get_solution_expand(n_winding, I_mat, sym_tmp)
        V_mat = _get_solution_expand(n_winding, V_mat, sym_tmp)

    # remove redundant solutions
    IV_mat = np.vstack((I_mat, V_mat))
    (_, idx) = np.unique(IV_mat, axis=1, return_index=True)
    I_mat = I_mat[:, idx]
    V_mat = V_mat[:, idx]

    # get the number of solutions for the full problem
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