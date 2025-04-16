"""
Module for generating correct value for the tests.
The values are extracted from the mesher and solver results.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"


def _get_mesher(data_voxel):
    """
    Get the results produced by the mesher.
    """

    # extract the data
    n_total = data_voxel["voxel_status"]["n_total"]
    n_used = data_voxel["voxel_status"]["n_used"]

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
    solution_ok = data_sweep["solution_ok"]
    P_total = data_sweep["integral_total"]["P_total"]
    W_total = data_sweep["integral_total"]["W_total"]

    # assemble results
    solver = {
        "freq": float(freq),
        "solution_ok": bool(solution_ok),
        "P_total": float(P_total),
        "W_total": float(W_total),
    }

    return solver


def generate_results(data_voxel, data_solution):
    """
    Get the results.
    """

    # extract the data
    meta_voxel = data_voxel["meta"]
    data_voxel = data_voxel["data"]
    assert isinstance(meta_voxel, dict), "invalid solution"
    assert isinstance(data_voxel, dict), "invalid solution"

    # extract the data
    meta_solution = data_solution["meta"]
    data_solution = data_solution["data"]
    assert isinstance(meta_solution, dict), "invalid solution"
    assert isinstance(data_solution, dict), "invalid solution"

    # extract the data
    status = data_solution["status"]
    data_init = data_solution["data_init"]
    data_sweep = data_solution["data_sweep"]

    # check solution
    assert status, "invalid solution"
    assert isinstance(data_init, dict), "invalid solution"
    assert isinstance(data_sweep, dict), "invalid solution"

    # check the mesher
    mesher = _get_mesher(data_voxel)

    # check the solver
    solver = {}
    for tag, data_sweep_tmp in data_sweep.items():
        solver[tag] = _get_solver(data_sweep_tmp)

    return mesher, solver
