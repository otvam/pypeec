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


def _get_excitation_compact(data, symmetry):
    """
    Reduce a matrix with respect to a particular symmetry.
    Only a single excitation per symmetry is kept.
    """

    # extract
    perm = symmetry["perm"]
    ref = symmetry["ref"]

    # cast and check
    perm = np.array(perm, dtype=int)
    if ref >= len(perm):
        raise ValueError("invalid index")

    # combine excitations with the symmetry
    for perm_tmp in perm:
        data[perm_tmp] = data[perm[ref]]

    return data


def _get_solution_expand(n_winding, data, symmetry):
    """
    Expand a matrix with respect to a particular symmetry.
    Different solutions are generated with permutations.
    The permutations are given by the symmetry.
    """

    # extract
    perm = symmetry["perm"]
    ref = symmetry["ref"]

    # cast and check
    perm = np.array(perm, dtype=int)
    if ref >= len(perm):
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


def get_excitation_all(n_winding, symmetry):
    """
    Determine which simulations are required to extract the full impedance matrix.
    The different symmetries are used to reduce the number of simulations.
    """

    # full excitations
    excitation = np.arange(n_winding)

    # combine excitations with the symmetries
    for symmetry_tmp in symmetry:
        excitation = _get_excitation_compact(excitation, symmetry_tmp)

    # remove redundant excitations
    excitation = np.unique(excitation)

    # get the number of solutions for the reduced problem
    n_solution = len(excitation)

    return n_solution, excitation


def get_solution_all(terminal, symmetry):
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
    for sym_tmp in symmetry:
        I_mat = _get_solution_expand(n_winding, I_mat, sym_tmp)
        V_mat = _get_solution_expand(n_winding, V_mat, sym_tmp)

    # remove redundant solutions
    IV_mat = np.vstack((I_mat, V_mat))
    (n_terminal, n_solution) = IV_mat.shape
    assert n_terminal == (2*n_winding), "invalid solution: terminal matrix shape"

    # update terminal
    terminal = {
        "n_winding": n_winding,
        "n_solution": n_solution,
        "freq": freq,
        "I_mat": I_mat,
        "V_mat": V_mat,
    }

    return terminal
