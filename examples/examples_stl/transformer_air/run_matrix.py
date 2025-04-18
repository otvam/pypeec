"""
Extract the impedance matrix from the solution:
    - Extract the terminal data (currents and voltages) from the solution.
    - Expand the extracted terminal data with the given symmetries.
    - Extract the impedance matrix from the terminal data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

# base packages
import os
import scilogger
import scisave
import pypeec

# import utils to be demonstrated
from pypeec.utils import matrix

# get a logger
LOGGER = scilogger.get_logger(__name__, "script")

# get the path the folder
PATH_ROOT = os.path.dirname(__file__)


def _solve_peec(folder_example, folder_config):
    """
    Solve the PEEC problem (mesher and solver).
    """

    # define the input
    file_geometry = os.path.join(folder_example, "geometry.yaml")
    file_problem = os.path.join(folder_example, "problem.yaml")
    file_tolerance = os.path.join(folder_config, "tolerance.yaml")

    # load the input
    data_geometry = scisave.load_config(file_geometry)
    data_problem = scisave.load_config(file_problem)
    data_tolerance = scisave.load_config(file_tolerance)

    # run the workflow (mesher and solver)
    data_voxel = pypeec.run_mesher_data(
        data_geometry=data_geometry,
    )
    data_solution = pypeec.run_solver_data(
        data_voxel=data_voxel,
        data_problem=data_problem,
        data_tolerance=data_tolerance,
    )

    return data_solution


def _show_matrix(matrix):
    """
    Print the content of an impedance matrix.
    """

    LOGGER.info("n_winding = %d", matrix["n_winding"])
    LOGGER.info("n_solution = %d", matrix["n_solution"])
    LOGGER.info("freq = %.2f kHz", 1e-3 * matrix["freq"])
    LOGGER.info("impedance matrix")
    with LOGGER.BlockIndent():
        LOGGER.info("Z_re_mat = %s Ohm", matrix["Z_mat"].real.tolist())
        LOGGER.info("Z_im_mat = %s Ohm", matrix["Z_mat"].imag.tolist())
    LOGGER.info("resistance / inductance matrix")
    with LOGGER.BlockIndent():
        LOGGER.info("R_mat = %s mOhm", (1e3 * matrix["R_mat"]).tolist())
        LOGGER.info("L_mat = %s nH", (1e9 * matrix["L_mat"]).tolist())
    LOGGER.info("coupling / quality matrix")
    with LOGGER.BlockIndent():
        LOGGER.info("k_R_mat = %s %%", (1e2 * matrix["k_R_mat"]).tolist())
        LOGGER.info("k_L_mat = %s %%", (1e2 * matrix["k_L_mat"]).tolist())
        LOGGER.info("Q_vec = %s p.u.", (1e0 * matrix["Q_vec"]).tolist())


if __name__ == "__main__":
    # ########################################################
    # ### solve the PEEC problem
    # ########################################################

    # folder containing the example files
    folder_example = os.path.join(PATH_ROOT, ".")

    # folder containing the global configuration files
    folder_config = os.path.join(PATH_ROOT, "..", "..", "config")

    # solve the PEEC problem
    data_solution = _solve_peec(folder_example, folder_config)

    # ########################################################
    # ### definition of the parameters
    # ########################################################

    # list of sweeps for the DC impedance matrix
    sweep_list_dc = ["sim_dc"]

    # list of sweeps for the AC impedance matrix
    sweep_list_ac = ["sim_ac"]

    # definition of the terminals for the impedance matrix
    terminal_list = [
        {"src": "pri_src", "sink": "pri_sink"},
        {"src": "sec_src", "sink": "sec_sink"},
    ]

    # definition of a list of permutations with the symmetries
    symmetry = [[0, 1], [1, 0]]

    # ########################################################
    # ### extract the impedance matrix
    # ########################################################

    # compute the impedance matrix
    LOGGER.info("compute the impedance matrix")
    with LOGGER.BlockIndent():
        LOGGER.info("extract the terminal data")
        terminal_dc = matrix.get_extract(data_solution, sweep_list_dc, terminal_list)
        terminal_ac = matrix.get_extract(data_solution, sweep_list_ac, terminal_list)

        LOGGER.info("expand with the symmetries")
        terminal_dc = matrix.get_symmetry(terminal_dc, symmetry)
        terminal_ac = matrix.get_symmetry(terminal_ac, symmetry)

        LOGGER.info("extract the impedance matrix")
        matrix_dc = matrix.get_matrix(terminal_dc)
        matrix_ac = matrix.get_matrix(terminal_ac)

    # print the DC results
    LOGGER.info("DC solution")
    with LOGGER.BlockIndent():
        _show_matrix(matrix_dc)

    # print the AC results
    LOGGER.info("AC solution")
    with LOGGER.BlockIndent():
        _show_matrix(matrix_ac)
