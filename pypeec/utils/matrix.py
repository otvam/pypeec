"""
Module for extracting the impedance matrix from the solver solution.

The following procedure is used:
    - extract the terminal data (currents and voltages) from the solution
    - expand the extracted terminal data with the given symmetries
    - extract the impedance matrix from the terminal data

For the impedance matrix, the following method is used:
    - components with an arbitrary number of terminals can be handled
    - an equation system is formed with all the terminal quantities
    - the least-square solution of the system is computed

The impedance matrix is post-processed:
    - computation of the resistance matrix
    - computation of the inductance matrix
    - computation of the quality factors
    - computation of the couplings
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import numpy as np
import numpy.linalg as lna


def _get_matrix_idx(n_winding):
    """
    Mapping of the impedance coefficients into a vector.
    The indices (row and column) of the impedance coefficients are returned.
    The impedance matrix is symmetric and only the independent coefficients are considered.
    """

    var_idx = []
    for i in range(n_winding):
        for j in range(i + 1):
            var_idx.append([i, j])

    return var_idx


def _get_matrix_assign(n_winding, var_idx, sol):
    """
    Assign the full impedance matrix from the coefficients.
    The coefficients are given in a vector.
    """

    mat = np.zeros((n_winding, n_winding), dtype=np.complex128)
    for i, (idx_i_1, idx_i_2) in enumerate(var_idx):
        mat[idx_i_1, idx_i_2] = sol[i]
        mat[idx_i_2, idx_i_1] = sol[i]

    return mat


def _get_matrix_eqn(n_winding, var_idx, I_vec):
    """
    Create the equation matrix for a given current excitation.
    """

    eqn_mat = np.zeros((n_winding, len(var_idx)), dtype=np.complex128)
    for i, (idx_i_1, idx_i_2) in enumerate(var_idx):
        eqn_mat[idx_i_1, i] = I_vec[idx_i_2]
        eqn_mat[idx_i_2, i] = I_vec[idx_i_1]

    return eqn_mat


def _get_matrix_coupling(n_winding, RL_mat):
    """
    Get the coupling matrix between the windings.
    """

    k_mat = np.zeros((n_winding, n_winding), dtype=np.float64)
    for i in range(n_winding):
        for j in range(n_winding):
            k_mat[i, j] = np.abs(RL_mat[i, j]) / np.sqrt(RL_mat[i, i] * RL_mat[j, j])
            k_mat[j, i] = np.abs(RL_mat[j, i]) / np.sqrt(RL_mat[i, i] * RL_mat[j, j])

    return k_mat


def _get_matrix_solve(terminal):
    """
    Extract the impedance matrix of the component.
    The impedance matrix is computed with a linear equation system.
    The equation system is built with the following complex variables:
        - matrix: current excitations
        - right-hand side: voltage excitations
        - solution: impedance coefficients
    """

    # extract the data
    n_solution = terminal["n_solution"]
    n_winding = terminal["n_winding"]
    freq = terminal["freq"]
    V_mat = terminal["V_mat"]
    I_mat = terminal["I_mat"]

    # check size
    assert I_mat.shape == (n_winding, n_solution), "invalid solution: current matrix shape"
    assert V_mat.shape == (n_winding, n_solution), "invalid solution: voltage matrix shape"

    # get the matrix size and indices of the coefficients
    var_idx = _get_matrix_idx(n_winding)

    # init the matrices
    rhs_vec = np.zeros(0, dtype=np.complex128)
    eqn_mat = np.zeros((0, len(var_idx)), dtype=np.complex128)

    # get the matrices
    for i in range(n_solution):
        # extract the data
        V_vec = V_mat[:, i]
        I_vec = I_mat[:, i]

        # get the equation matrix
        eqn_tmp = _get_matrix_eqn(n_winding, var_idx, I_vec)

        # append the data
        rhs_vec = np.concatenate((rhs_vec, V_vec))
        eqn_mat = np.concatenate((eqn_mat, eqn_tmp))

    # check system size
    assert len(rhs_vec) >= len(var_idx), "invalid solution: number of equation is too low"

    # check system rank
    assert lna.matrix_rank(eqn_mat) == len(var_idx), "invalid solution: system rank is insufficient"

    # extraction impedance coefficients with a least-square solution
    (sol, _, _, _) = lna.lstsq(eqn_mat, rhs_vec, rcond=None)

    # assign the coefficients to the full impedance matrix
    Z_mat = _get_matrix_assign(n_winding, var_idx, sol)

    return n_winding, n_solution, freq, Z_mat


def _get_matrix_parse(n_winding, n_solution, freq, Z_mat):
    """
    Get the equivalent circuit of the component from the impedance matrix.
    """

    # angular frequency
    w = 2 * np.pi * freq

    # get the resistance
    R_mat = np.real(Z_mat)

    # get the inductance
    if freq == 0:
        L_mat = np.full(Z_mat.shape, np.nan)
    else:
        L_mat = np.imag(Z_mat) / w

    # get the quality factor
    Q_mat = (w * L_mat) / R_mat
    Q_vec = np.diagonal(Q_mat)

    # get the coupling
    k_R_mat = _get_matrix_coupling(n_winding, R_mat)
    k_L_mat = _get_matrix_coupling(n_winding, L_mat)

    # assign the results
    matrix = {
        "freq": freq,
        "n_winding": n_winding,
        "n_solution": n_solution,
        "Z_mat": Z_mat,
        "R_mat": R_mat,
        "L_mat": L_mat,
        "k_R_mat": k_R_mat,
        "k_L_mat": k_L_mat,
        "Q_vec": Q_vec,
    }

    return matrix


def _get_symmetry_expand(data, symmetry):
    """
    Expand a matrix with respect to a particular symmetry.
    Different solutions are generated with permutations.
    """

    # cast and check
    symmetry = np.array(symmetry, dtype=int)

    # initialize the expanded matrix
    data_all = np.zeros((len(data), 0), dtype=np.complex128)

    # expand the matrix with the symmetries
    for perm in symmetry:
        # get the permutation to be performed
        data_all = np.hstack((data_all, data[perm]))

    return data_all


def _get_extract_sweep(source, terminal_list):
    """
    Get the terminal currents and voltages for a specific sweep.
    """

    # init list
    V_vec = np.zeros(len(terminal_list), dtype=np.complex128)
    I_vec = np.zeros(len(terminal_list), dtype=np.complex128)

    # get the solution
    for idx, terminal in enumerate(terminal_list):
        # extract the terminal name
        src = terminal["src"]
        sink = terminal["sink"]

        # extract the terminal quantities
        V_vec[idx] = source[src]["V"] - source[sink]["V"]
        I_vec[idx] = (source[src]["I"] - source[sink]["I"]) / 2

    # assign the data
    V_vec = np.array(V_vec, dtype=np.complex128)
    I_vec = np.array(I_vec, dtype=np.complex128)

    return V_vec, I_vec


def get_matrix(terminal):
    """
    Extract the impedance matrix from the terminal data.
    """

    # get the impedance matrix
    (n_winding, n_solution, freq, Z_mat) = _get_matrix_solve(terminal)

    # get the complete circuit
    matrix = _get_matrix_parse(n_winding, n_solution, freq, Z_mat)

    return matrix


def get_symmetry(terminal, symmetry):
    """
    Expand the extracted terminal data with the given symmetries.
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
    I_mat = _get_symmetry_expand(I_mat, symmetry)
    V_mat = _get_symmetry_expand(V_mat, symmetry)

    # remove redundant solutions
    IV_mat = np.vstack((I_mat, V_mat))
    (n_terminal, n_solution) = IV_mat.shape
    assert n_terminal == (2 * n_winding), "invalid solution: terminal matrix shape"

    # update terminal
    terminal = {
        "n_winding": n_winding,
        "n_solution": n_solution,
        "freq": freq,
        "I_mat": I_mat,
        "V_mat": V_mat,
    }

    return terminal


def get_extract(data_solution, sweep_list, terminal_list):
    """
    Extract the terminal data (currents and voltages) from the solution.
    """

    # extract the data
    data_init = data_solution["data_init"]
    data_sweep = data_solution["data_sweep"]

    # check solution
    assert isinstance(data_init, dict), "invalid solution"
    assert isinstance(data_sweep, dict), "invalid solution"

    # get the matrix sizes
    n_solution = len(sweep_list)
    n_winding = len(terminal_list)

    # initialize the matrix
    V_mat = np.zeros((n_winding, n_solution), dtype=np.complex128)
    I_mat = np.zeros((n_winding, n_solution), dtype=np.complex128)
    freq_vec = np.zeros(n_solution, dtype=np.float64)

    # extract data
    for idx, sweep in enumerate(sweep_list):
        # extract the data
        data_sweep_tmp = data_sweep[sweep]
        freq = data_sweep_tmp["freq"]
        source = data_sweep_tmp["source"]

        # compute
        (V_vec, I_vec) = _get_extract_sweep(source, terminal_list)

        # assign
        V_mat[:, idx] = V_vec
        I_mat[:, idx] = I_vec
        freq_vec[idx] = freq

    # get and check frequency
    freq = np.mean(freq_vec)
    assert np.allclose(freq_vec, freq), "invalid solution: invalid frequency"

    # create data
    terminal = {
        "n_solution": n_solution,
        "n_winding": n_winding,
        "V_mat": V_mat,
        "I_mat": I_mat,
        "freq": freq,
    }

    return terminal
