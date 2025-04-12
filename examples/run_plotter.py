"""
User script for plotting the solution of a PEEC problem.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import os.path
import pypeec
import examples_config

# get the path of the root of the code
PATH_ROOT = os.path.dirname(__file__)

# get config
FOLDER_CONFIG = examples_config.FOLDER_CONFIG
FOLDER_EXAMPLE = examples_config.FOLDER_EXAMPLE


if __name__ == "__main__":
    # get the filenames
    file_solution = os.path.join(PATH_ROOT, FOLDER_EXAMPLE, "solution.json.gz")
    file_plotter = os.path.join(PATH_ROOT, FOLDER_CONFIG, "plotter.yaml")

    # list of plots to be shown (defined in plotter.yaml)
    tag_plot = [
        "V_c_norm",
        "J_c_norm",
        "H_p_norm",
        "residuum",
    ]

    # method used for rendering the plots
    plot_mode = "qt"

    # run
    pypeec.run_plotter_file(
        file_solution=file_solution,
        file_plotter=file_plotter,
        tag_plot=tag_plot,
        plot_mode=plot_mode,
    )
