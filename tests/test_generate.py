"""
Module for generating correct value for the tests.
The values are extracted from the mesher and solver results.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"


def _get_mesher(voxel_status):
    """
    Get the results produced by the mesher.
    """

    # extract data
    n_total = voxel_status["n_total"]
    n_used = voxel_status["n_used"]

    # assemble results
    mesher = {
        "n_total": int(n_total),
        "n_used": int(n_used),
    }

    return mesher


def _get_solver(data_run):
    """
    Get the results produced by the solver.
    """

    # extract data
    freq = data_run["freq"]
    has_converged = data_run["has_converged"]
    P_tot = data_run["integral"]["P_tot"]
    W_tot = data_run["integral"]["W_tot"]

    # assemble results
    solver = {
        "freq": float(freq),
        "has_converged": bool(has_converged),
        "P_tot": float(P_tot),
        "W_tot": float(W_tot),
    }

    return solver


def generate_results(voxel_status, data_run):
    """
    Get the results.
    """

    # check the mesher
    mesher = _get_mesher(voxel_status)

    # check the solver
    solver = {}
    for tag, data_run_tmp in data_run.items():
        solver[tag] = _get_solver(data_run_tmp)

    return mesher, solver
