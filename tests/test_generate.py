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
    P_tot = data_sweep["integral"]["P_tot"]
    W_tot = data_sweep["integral"]["W_tot"]

    # assemble results
    solver = {
        "freq": float(freq),
        "has_converged": bool(has_converged),
        "P_tot": float(P_tot),
        "W_tot": float(W_tot),
    }

    return solver


def generate_results(data_geom, data_sweep):
    """
    Get the results.
    """

    # check the mesher
    mesher = _get_mesher(data_geom)

    # check the solver
    solver = {}
    for tag, data_sweep_tmp in data_sweep.items():
        solver[tag] = _get_solver(data_sweep_tmp)

    return mesher, solver
