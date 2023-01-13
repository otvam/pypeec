"""
Integration test for the solver and plotter.
True unit tests are not implemented.

The testing is done with the unittest library.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import unittest
import tempfile
import logging
from PyPEEC import script

# disable logging to prevent clutter during test evaluation
logging.disable(logging.CRITICAL)


class TestSum(unittest.TestCase):
    """
    Test solver/plotter for different cases.
    """

    def _test_solver_plotter(self, name):
        """
        Test solver/plotter for a specific test case.
        """

        # get input file name
        file_voxel = "tests/data_voxel/%s.pck" % name
        file_problem = "tests/data_problem/%s.json" % name
        file_plotter = "tests/data_viewer_plotter/data_plotter.json"

        # create the temporary output file
        with tempfile.NamedTemporaryFile(suffix='.pck') as fid_solution:
            # get the temped file name
            file_solution = fid_solution.name

            # run the mesher
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
