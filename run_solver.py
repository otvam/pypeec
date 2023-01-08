"""
User script for solving a problem with the FFT-PEEC solver.
Contain the program entry point.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import sys
import pickle

from main import solver


def get_data_solver_simple():
    """
    Get the data for a simple problem.
    """

    # add the module to the namespace
    from data_input import data_solver_simple

    # get the data
    data_solver = data_solver_simple.get_data()

    return data_solver


def get_data_solver_pcb_trf():
    """
    Get the data for a PCB transformer.
    """

    # add the module to the namespace
    from data_input import data_solver_pcb_trf

    # get the data
    data_solver = data_solver_pcb_trf.get_data()

    return data_solver


def run(name, data_solver):
    """
    Solve the problem and write the result file.
    """

    # call solver
    (status, data_res) = solver.run(data_solver)

    # save results
    filename = "data_output/%s.pck" % name
    with open(filename, "wb") as fid:
        pickle.dump(data_res, fid)

    # exit
    exit_code = int(not status)

    return exit_code


if __name__ == "__main__":
    # name of the simulation
    name = "data_pcb_trf"

    # get the data
    if name == "data_simple":
        data_solver = get_data_solver_simple()
    elif name == "data_pcb_trf":
        data_solver = get_data_solver_pcb_trf()
    else:
        raise ValueError("invalid name")

    # run
    exit_code = run(name, data_solver)
    sys.exit(exit_code)
