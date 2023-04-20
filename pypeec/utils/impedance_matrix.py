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


def _get_load_terminal(freq, source, has_converged, winding):
    # init list
    voltage = []
    current = []

    # extract data
    for dat_tmp in winding:
        src = dat_tmp["src"]
        sink = dat_tmp["sink"]

        V_tmp = source[src]["V"] - source[sink]["V"]
        I_tmp = (source[src]["I"] - source[sink]["I"]) / 2

        voltage.append(V_tmp)
        current.append(I_tmp)

    # extract data
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

    # extract data
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


def get_coupling_matrix(n_mat, RL_mat):
    k_mat = np.zeros((n_mat, n_mat), dtype=np.float_)
    for i in range(n_mat):
        for j in range(n_mat):
            k_mat[i, j] = RL_mat[i, j]/np.sqrt(RL_mat[i, i]*RL_mat[j, j])
            k_mat[j, i] = RL_mat[j, i]/np.sqrt(RL_mat[i, i]*RL_mat[j, j])

    return k_mat


def get_circuit_matrix(n_mat, freq, res):
    """
    Get the equivalent circuit of the component.
    """

    # angular frequency
    w = 2*np.pi*freq

    # get the inductance and resistance
    R_mat = np.real(res)
    L_mat = np.imag(res)/w

    # # get the quality factor
    Q_mat = (w*L_mat)/R_mat

    # get the coupling
    k_R_mat = get_coupling_matrix(n_mat, R_mat)
    k_L_mat = get_coupling_matrix(n_mat, L_mat)

    # assign the results
    data_matrix = {
        "freq": freq, "R_mat": R_mat, "L_mat": L_mat,
        "k_R_mat": k_R_mat, "k_L_mat": k_L_mat, "Q_mat": Q_mat,
    }

    return data_matrix


def _get_idx_matrix(n_mat):
    # array with the indices
    var_idx = []

    # creating a matrix mapping the following indices:
    for i in range(n_mat):
        for j in range(i+1):
            var_idx.append([i, j])

    return var_idx


def _get_assign_matrix(n_mat, var_idx, sol):
    res = np.zeros((n_mat, n_mat), dtype=np.complex_)
    for i, (idx_i_1, idx_i_2) in enumerate(var_idx):
        res[idx_i_1, idx_i_2] = sol[i]
        res[idx_i_2, idx_i_1] = sol[i]

    return res


def _get_eqn_matrix(n_mat, var_idx, current):
    eqn = np.zeros((n_mat, len(var_idx)), dtype=np.complex_)
    for i, (idx_i_1, idx_i_2) in enumerate(var_idx):
        eqn[idx_i_1, i] = current[idx_i_2]
        eqn[idx_i_2, i] = current[idx_i_1]

    return eqn


def _get_solve_matrix(n_mat, terminal, sweep_list, tol):
    """
    Extract the impedance matrix of the component.
    """

    # get the matrix size and indices
    var_idx = _get_idx_matrix(n_mat)

    # init the matrices
    freq_vec = np.zeros(0, dtype=np.float_)
    rhs_vec = np.zeros(0, dtype=np.complex_)
    eqn_mat = np.zeros((0, len(var_idx)), dtype=np.complex_)

    # get the matrices
    for tag in sweep_list:
        solution_tmp = terminal[tag]
        freq = solution_tmp["freq"]
        has_converged = solution_tmp["has_converged"]
        voltage = solution_tmp["voltage"]
        current = solution_tmp["current"]

        # check convergence
        assert has_converged, "invalid solution: convergence issue"

        # assign the equation matrix
        eqn = _get_eqn_matrix(n_mat, var_idx, current)

        # append the data
        freq_vec = np.append(freq_vec, freq)
        rhs_vec = np.concatenate((rhs_vec, voltage), axis=0)
        eqn_mat = np.concatenate((eqn_mat, eqn), axis=0)

    # check frequency
    assert np.ptp(freq_vec) < tol["tol_freq"], "invalid solution: residuum issue"

    # check system size
    assert len(rhs_vec) >= len(var_idx), "invalid solution: number of equation is too low"

    # check system rank
    assert lna.matrix_rank(eqn_mat) == len(var_idx),  "invalid solution: system rank is insufficient"

    # compute the frequency
    freq = np.mean(freq_vec)

    # extraction impedance
    (sol, res, _, _) = lna.lstsq(eqn_mat, rhs_vec, rcond=None)

    # check residuum
    assert res < tol["tol_res"], "invalid solution: residuum issue"

    # assign the impedance matrix
    res = _get_assign_matrix(n_mat, var_idx, sol)

    return freq, res


def get_extract(data_solution, winding, sweep, tol):
    """
    Extract the equivalent circuit of a component.
    """

    # extract data
    (n_mat, terminal) = _get_load_solution(data_solution, winding)

    # init results
    data_matrix = {}

    # fill the data
    for tag, sweep_list in sweep.items():
        # get the impedance
        (freq, res) = _get_solve_matrix(n_mat, terminal, sweep_list, tol)

        # get the complete circuit
        data_matrix_tmp = get_circuit_matrix(n_mat, freq, res)

        # assign the data
        data_matrix[tag] = data_matrix_tmp

    return data_matrix
