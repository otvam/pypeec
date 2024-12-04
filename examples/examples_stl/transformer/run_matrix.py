"""
Extract the impedance matrix from the solution:
    - extract the terminal data (currents and voltages) from the solution
    - expand the extracted terminal data with the given symmetries
    - extract the impedance matrix from the terminal data

This script is loading and post-processing the solver results.
Before running this script, the PyPEEC mesher and solver should be run.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import sys
import scisave
from pypeec.utils import matrix


def _show_matrix(name, matrix):
    """
    Print the content of an impedance matrix.
    """

    # load the images
    print(name)
    print("    n_winding = %d" % matrix["n_winding"])
    print("    n_solution = %d" % matrix["n_solution"])
    print("    freq = %.2f kHz" % (1e-3*matrix["freq"]))
    print("    impedance matrix")
    print("        Z_re_mat = %s Ohm" % matrix["Z_mat"].real.tolist())
    print("        Z_im_mat = %s Ohm" % matrix["Z_mat"].imag.tolist())
    print("    resistance / inductance matrix")
    print("        R_mat = %s mOhm" % (1e3*matrix["R_mat"]).tolist())
    print("        L_mat = %s nH" % (1e9*matrix["L_mat"]).tolist())
    print("    coupling / quality matrix")
    print("        k_R_mat = %s %%" % (1e2*matrix["k_R_mat"]).tolist())
    print("        k_L_mat = %s %%" % (1e2*matrix["k_L_mat"]).tolist())
    print("        Q_mat = %s p.u." % (1e0*matrix["Q_mat"]).tolist())


if __name__ == "__main__":
    # ########################################################
    # ### definition of the parameters
    # ########################################################

    # name of the solution file
    filename = "solution.json.gz"

    # list of sweeps for used for the DC impedance matrix
    sweep_list_dc = [
        "sim_dc",
    ]

    # list of sweeps for used for the AC impedance matrix
    sweep_list_ac = [
        "sim_ac",
    ]

    # definition of the terminals for the impedance matrix
    terminal_list = [
        {"src": "pri_src", "sink": "pri_sink"},
        {"src": "sec_src", "sink": "sec_sink"},
    ]

    # definition of a list of permutations defining the symmetries
    symmetry = [
        [[0, 1], [1, 0]],
    ]

    # ########################################################
    # ### extract the impedance matrix
    # ########################################################

    # load the solution
    data_solution = scisave.load_data(filename)

    # extract the terminal data
    terminal_dc = matrix.get_extract(data_solution, sweep_list_dc, terminal_list)
    terminal_ac = matrix.get_extract(data_solution, sweep_list_ac, terminal_list)

    # expand the extracted data with the symmetries
    terminal_dc = matrix.get_symmetry(terminal_dc, symmetry)
    terminal_ac = matrix.get_symmetry(terminal_ac, symmetry)

    # extract the impedance matrix
    matrix_dc = matrix.get_matrix(terminal_dc)
    matrix_ac = matrix.get_matrix(terminal_ac)

    # print the results
    _show_matrix("DC solution", matrix_dc)
    _show_matrix("AC solution", matrix_ac)

    # exit
    sys.exit(0)
