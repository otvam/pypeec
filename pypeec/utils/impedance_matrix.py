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
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import numpy as np
import numpy.linalg as lna


def _get_idx_matrix(n_mat):
    """
    Mapping of the impedance coefficients into a vector.
    The indices (row and column) of the impedance coefficients are returned.
    The impedance matrix is symmetric and only the independent coefficients are considered.

    """

    var_idx = []
    for i in range(n_mat):
        for j in range(i+1):
            var_idx.append([i, j])

    return var_idx


def _get_assign_matrix(n_mat, var_idx, sol):
    """
    Assign the full impedance matrix from the coefficients.
    The coefficients are given in a vector.
    """

    mat = np.zeros((n_mat, n_mat), dtype=np.complex_)
    for i, (idx_i_1, idx_i_2) in enumerate(var_idx):
        mat[idx_i_1, idx_i_2] = sol[i]
        mat[idx_i_2, idx_i_1] = sol[i]

    return mat


def _get_eqn_matrix(n_mat, var_idx, current):
    """
    Create the equation matrix for a given current excitation.
    """

    eqn = np.zeros((n_mat, len(var_idx)), dtype=np.complex_)
    for i, (idx_i_1, idx_i_2) in enumerate(var_idx):
        eqn[idx_i_1, i] = current[idx_i_2]
        eqn[idx_i_2, i] = current[idx_i_1]

    return eqn


def _get_solve_matrix(n_mat, terminal, condition_list, tol):
    """
    Extract the impedance matrix of the component.

    The impedance matrix is computed with a linear equation system.
    The equation system is built with the following variable:
        - matrix: current excitations
        - right-hand side: voltage excitations
        - solution: impedance coefficients
    """

    # extract the data
    tol_res = tol["tol_res"]
    tol_freq = tol["tol_freq"]
    check_convergence = tol["check_convergence"]

    # get the matrix size and indices of the coefficients
    var_idx = _get_idx_matrix(n_mat)

    # init the matrices
    freq_vec = np.zeros(0, dtype=np.float_)
    rhs_vec = np.zeros(0, dtype=np.complex_)
    eqn_mat = np.zeros((0, len(var_idx)), dtype=np.complex_)

    # get the matrices
    for tag in condition_list:
        # extract the data
        solution_tmp = terminal[tag]
        freq = solution_tmp["freq"]
        has_converged = solution_tmp["has_converged"]
        voltage = solution_tmp["voltage"]
        current = solution_tmp["current"]

        # check convergence
        if check_convergence:
            assert has_converged, "invalid solution: convergence issue"

        # get the equation matrix
        eqn = _get_eqn_matrix(n_mat, var_idx, current)

        # append the data
        freq_vec = np.append(freq_vec, freq)
        rhs_vec = np.concatenate((rhs_vec, voltage), axis=0)
        eqn_mat = np.concatenate((eqn_mat, eqn), axis=0)

    # check that the frequency is constant
    assert np.ptp(freq_vec) < tol_freq, "invalid solution: residuum issue"

    # compute the frequency
    freq = np.mean(freq_vec)

    # check system size
    assert len(rhs_vec) >= len(var_idx), "invalid solution: number of equation is too low"

    # check system rank
    assert lna.matrix_rank(eqn_mat) == len(var_idx),  "invalid solution: system rank is insufficient"

    # extraction impedance coefficients with a least-square solution
    (sol, res, _, _) = lna.lstsq(eqn_mat, rhs_vec, rcond=None)

    # check residuum
    assert np.all(res < tol_res), "invalid solution: residuum issue"

    # assign the coefficients to the full impedance matrix
    Z_mat = _get_assign_matrix(n_mat, var_idx, sol)

    return freq, Z_mat


def _get_coupling_matrix(n_mat, RL_mat):
    """
    Get the coupling matrix between the windings.
    """

    k_mat = np.zeros((n_mat, n_mat), dtype=np.float_)
    for i in range(n_mat):
        for j in range(n_mat):
            k_mat[i, j] = RL_mat[i, j]/np.sqrt(RL_mat[i, i]*RL_mat[j, j])
            k_mat[j, i] = RL_mat[j, i]/np.sqrt(RL_mat[i, i]*RL_mat[j, j])

    return k_mat


def _get_circuit(n_mat, freq, Z_mat):
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
    k_R_mat = _get_coupling_matrix(n_mat, R_mat)
    k_L_mat = _get_coupling_matrix(n_mat, L_mat)

    # assign the results
    data_matrix = {
        "freq": freq, "Z_mat": Z_mat, "R_mat": R_mat, "L_mat": L_mat,
        "k_R_mat": k_R_mat, "k_L_mat": k_L_mat, "Q_mat": Q_mat,
    }

    return data_matrix


def _get_load_terminal(freq, source, has_converged, winding):
    """
    Get the terminal currents and voltages for a specific sweep.
    """

    # init list
    voltage = []
    current = []

    # get the solution
    for dat_tmp in winding:
        # extract the terminal name
        src = dat_tmp["src"]
        sink = dat_tmp["sink"]

        # extract the terminal quantities
        V_tmp = source[src]["V"] - source[sink]["V"]
        I_tmp = (source[src]["I"] - source[sink]["I"]) / 2

        # add the quantities
        voltage.append(V_tmp)
        current.append(I_tmp)

    # assign the data
    current = np.array(current, dtype=np.complex_)
    voltage = np.array(voltage, dtype=np.complex_)

    # assign
    terminal = {
        "freq": freq, "has_converged": has_converged,
        "voltage": voltage, "current": current,
    }

    return terminal


def _get_load_solution(data_solution, winding):
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
    n_mat = len(winding)

    # extract data
    terminal = {}
    for tag, dat_tmp in data_sweep.items():
        # extract the data
        freq = dat_tmp["freq"]
        source = dat_tmp["source"]
        has_converged = dat_tmp["has_converged"]

        # assign
        terminal[tag] = _get_load_terminal(freq, source, has_converged, winding)

    return n_mat, terminal


def get_extract(data_solution, winding, condition, tol):
    """
    Extract the equivalent circuit of a component.
    """

    # extract terminal behaviour from the solution
    (n_mat, terminal) = _get_load_solution(data_solution, winding)

    # init results
    data_matrix = {}

    # get the data for each operating condition
    for tag, condition_list in condition.items():
        # get the impedance matrix
        (freq, res) = _get_solve_matrix(n_mat, terminal, condition_list, tol)

        # get the complete circuit
        data_matrix_tmp = _get_circuit(n_mat, freq, res)

        # assign the data
        data_matrix[tag] = data_matrix_tmp

    return data_matrix
