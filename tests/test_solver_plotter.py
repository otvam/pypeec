"""
Integration test for the solver and plotter.
True unit tests are not implemented.

The testing is done with the unittest library.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import os
import unittest
import tempfile
import logging
from PyPEEC import script

# disable logging to prevent clutter during test evaluation
logging.disable(logging.CRITICAL)

# get the path the folder
path_root = os.path.dirname(__file__)


class TestSolverPlotter(unittest.TestCase):
    """
    Test solver/plotter for different cases.
    """

    def _test_solver_plotter(self, name):
        """
        Test solver/plotter for a specific test case.
        """

        # get input file name
        file_voxel = os.path.join(path_root, "data_voxel", name + ".pck")
        file_problem = os.path.join(path_root, "data_problem", name + ".json")
        file_plotter = os.path.join(path_root, "data_viewer_plotter", "data_plotter.json")

        # create the temporary output file
        with tempfile.NamedTemporaryFile(suffix='.pck') as fid_solution:
            # get the temped file name
            file_solution = fid_solution.name

            # run the solver
            status = script.run_solver(file_voxel, file_problem, file_solution)
            self.assertTrue(status, msg="solver failure")

            # run the plotter
            status = script.run_plotter(file_solution, file_plotter, False)
            self.assertTrue(status, msg="plotter failure")

    def test_voxel_slab(self):
        """
        Test solver/plotter for voxel_slab.
        """

        self._test_solver_plotter("voxel_slab")

    def test_voxel_transformer(self):
        """
        Test solver/plotter for voxel_transformer.
        """

        self._test_solver_plotter("voxel_transformer")


if __name__ == '__main__':
    unittest.main()
