"""
User script for solving a problem with the FFT-PEEC lib_solver.
Contain the program entry point.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import sys
import pickle

from PyPEEC import solver


def run(name, data_solver):
    """
    Solve the problem and write the result file.
    """

    # call lib_solver
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
    name = "data_simple"

    # get the data
    if name == "data_test":
        from data_input import data_solver_test
        data_solver = data_solver_test.get_data()
    elif name == "data_simple":
        from data_input import data_solver_simple
        data_solver = data_solver_simple.get_data()
    elif name == "data_pcb_trf":
        from data_input import data_solver_pcb_trf
        data_solver = data_solver_pcb_trf.get_data()
    else:
        raise ValueError("invalid name")

    # run
    exit_code = run(name, data_solver)
    sys.exit(exit_code)
