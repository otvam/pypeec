"""
Module for extracting the impedance matrix from the solver solution.

The impedance matrix is extracted from the terminal currents and voltages.
An equation system is formed with all the terminal quantities.
The least-square solution of the system is computed.
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


def _get_idx_matrix(n_winding):
    """
    Mapping of the impedance coefficients into a vector.
    The indices (row and column) of the impedance coefficients are returned.
    The impedance matrix is symmetric and only the independent coefficients are considered.

    """

    var_idx = []
    for i in range(n_winding):
        for j in range(i+1):
            var_idx.append([i, j])

    return var_idx


def _get_assign_matrix(n_winding, var_idx, sol):
    """
    Assign the full impedance matrix from the coefficients.
    The coefficients are given in a vector.
    """

    mat = np.zeros((n_winding, n_winding), dtype=np.complex_)
    for i, (idx_i_1, idx_i_2) in enumerate(var_idx):
        mat[idx_i_1, idx_i_2] = sol[i]
        mat[idx_i_2, idx_i_1] = sol[i]

    return mat


def _get_eqn_matrix(n_winding, var_idx, I_vec):
    """
    Create the equation matrix for a given current excitation.
    """

    eqn_mat = np.zeros((n_winding, len(var_idx)), dtype=np.complex_)
    for i, (idx_i_1, idx_i_2) in enumerate(var_idx):
        eqn_mat[idx_i_1, i] = I_vec[idx_i_2]
        eqn_mat[idx_i_2, i] = I_vec[idx_i_1]

    return eqn_mat


def _get_solve_matrix(n_winding, terminal, extraction_tolerance):
    """
    Extract the impedance matrix of the component.

    The impedance matrix is computed with a linear equation system.
    The equation system is built with the following variable:
        - matrix: current excitations
        - right-hand side: voltage excitations
        - solution: impedance coefficients
    """

    # extract the data
    tol_res = extraction_tolerance["tol_res"]
    tol_freq = extraction_tolerance["tol_freq"]
    check_convergence = extraction_tolerance["check_convergence"]

    # get the matrix size and indices of the coefficients
    var_idx = _get_idx_matrix(n_winding)

    # init the matrices
    freq_vec = np.zeros(0, dtype=np.float_)
    rhs_vec = np.zeros(0, dtype=np.complex_)
    eqn_mat = np.zeros((0, len(var_idx)), dtype=np.complex_)

    # get the matrices
    for terminal_tmp in terminal:
        # extract the data
        freq = terminal_tmp["freq"]
        has_converged = terminal_tmp["has_converged"]
        V_vec = terminal_tmp["V_vec"]
        I_vec = terminal_tmp["I_vec"]

        # check convergence
        if check_convergence:
            assert has_converged, "invalid solution: convergence issue"

        # get the equation matrix
        eqn_tmp = _get_eqn_matrix(n_winding, var_idx, I_vec)

        # append the data
        freq_vec = np.append(freq_vec, freq)
        rhs_vec = np.concatenate((rhs_vec, V_vec), axis=0)
        eqn_mat = np.concatenate((eqn_mat, eqn_tmp), axis=0)

    # check that the frequency is constant
    assert np.ptp(freq_vec) < tol_freq, "invalid solution: invalid frequency"

    # compute the frequency
    freq = np.mean(freq_vec)

    # check that the frequency is positive
    assert freq > 0, "invalid solution: invalid frequency"

    # check system size
    assert len(rhs_vec) >= len(var_idx), "invalid solution: number of equation is too low"

    # check system rank
    assert lna.matrix_rank(eqn_mat) == len(var_idx),  "invalid solution: system rank is insufficient"

    # extraction impedance coefficients with a least-square solution
    (sol, res, _, _) = lna.lstsq(eqn_mat, rhs_vec, rcond=None)

    # check residuum
    assert np.all(res < tol_res), "invalid solution: residuum issue"

    # assign the coefficients to the full impedance matrix
    Z_mat = _get_assign_matrix(n_winding, var_idx, sol)

    return freq, Z_mat


def _get_coupling_matrix(n_winding, RL_mat):
    """
    Get the coupling matrix between the windings.
    """

    k_mat = np.zeros((n_winding, n_winding), dtype=np.float_)
    for i in range(n_winding):
        for j in range(n_winding):
            k_mat[i, j] = RL_mat[i, j]/np.sqrt(RL_mat[i, i]*RL_mat[j, j])
            k_mat[j, i] = RL_mat[j, i]/np.sqrt(RL_mat[i, i]*RL_mat[j, j])

    return k_mat


def _get_parse_matrix(n_winding, freq, Z_mat):
    """
    Get the equivalent circuit of the component from the impedance matrix.
    """

    # angular frequency
    w = 2*np.pi*freq

    # get the inductance and resistance
    R_mat = np.real(Z_mat)
    L_mat = np.imag(Z_mat)/w

    # # get the quality factor
    Q_mat = (w*L_mat)/R_mat

    # get the coupling
    k_R_mat = _get_coupling_matrix(n_winding, R_mat)
    k_L_mat = _get_coupling_matrix(n_winding, L_mat)

    # assign the results
    matrix = {
        "freq": freq, "Z_mat": Z_mat, "R_mat": R_mat, "L_mat": L_mat,
        "k_R_mat": k_R_mat, "k_L_mat": k_L_mat, "Q_mat": Q_mat,
    }

    return matrix


def get_extract(n_winding, terminal, extraction_tolerance):
    """
    Extract the equivalent circuit of a component.
    """

    # get the impedance matrix
    (freq, res) = _get_solve_matrix(n_winding, terminal, extraction_tolerance)

    # get the complete circuit
    matrix = _get_parse_matrix(n_winding, freq, res)

    return matrix
