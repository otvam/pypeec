"""
Module for generating correct value for the tests.
The values are extracted from the mesher and solver results.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"


def _get_mesher(data_geom):
    """
    Get the results produced by the mesher.
    """

    # extract the data
    n_total = data_geom["voxel_status"]["n_total"]
    n_used = data_geom["voxel_status"]["n_used"]

    # assemble results
    mesher = {
        "n_total": int(n_total),
        "n_used": int(n_used),
    }

    return mesher


def _get_solver(data_sweep):
    """
    Get the results produced by the solver.
    """

    # extract the data
    freq = data_sweep["freq"]
    has_converged = data_sweep["has_converged"]
    P_total = data_sweep["integral"]["P_total"]
    W_total = data_sweep["integral"]["W_total"]

    # assemble results
    solver = {
        "freq": float(freq),
        "has_converged": bool(has_converged),
        "P_total": float(P_total),
        "W_total": float(W_total),
    }

    return solver


def generate_results(data_voxel, data_solution):
    """
    Get the results.
    """

    # extract the data
    data_geom = data_voxel["data_geom"]
    data_sweep = data_solution["data_sweep"]

    # check the mesher
    mesher = _get_mesher(data_geom)

    # check the solver
    solver = {}
    for tag, data_sweep_tmp in data_sweep.items():
        solver[tag] = _get_solver(data_sweep_tmp)

    return mesher, solver
