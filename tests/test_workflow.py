"""
Integration test for the complete workflow.
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


class TestMesherViewer(unittest.TestCase):
    """
    Test the workflow different cases:
        - run the mesher
        - run the viewer
        - run the solver
        - run the plotter

    The intermediate file are stored with temporary files.
    """

    def _test_workflow(self, name):
        """
        Test mesher/viewer for a specific test case.
        """

        # get input file name
        file_mesher = os.path.join(path_root, name, "mesher.json")
        file_point = os.path.join(path_root, name, "point.json")
        file_problem = os.path.join(path_root, name, "problem.json")
        file_plotter = os.path.join(path_root, "visualization", "data_plotter.json")
        file_viewer = os.path.join(path_root, "visualization", "data_viewer.json")

        # get the temped file name
        fid_voxel = tempfile.NamedTemporaryFile(suffix='.pck')
        fid_solution = tempfile.NamedTemporaryFile(suffix='.pck')
        file_voxel = fid_voxel.name
        file_solution = fid_solution.name

        # run the mesher
        status = script.run_mesher(file_mesher, file_voxel)
        self.assertTrue(status, msg="mesher failure")

        # run the viewer
        status = script.run_viewer(file_voxel, file_point, file_viewer, False)
        self.assertTrue(status, msg="viewer failure")

        # run the solver
        status = script.run_solver(file_voxel, file_problem, file_solution)
        self.assertTrue(status, msg="solver failure")

        # run the plotter
        status = script.run_plotter(file_solution, file_point, file_plotter, False)
        self.assertTrue(status, msg="plotter failure")

    def test_png_inductor(self):
        """
        Test workflow for png_inductor.
        """

        self._test_workflow("png_inductor")

    def test_png_wire(self):
        """
        Test workflow for png_wire.
        """

        self._test_workflow("png_wire")

    def test_stl_inductor(self):
        """
        Test workflow for stl_inductor.
        """

        self._test_workflow("stl_inductor")

    def test_stl_transformer(self):
        """
        Test workflow for stl_transformer.
        """

        self._test_workflow("stl_transformer")

    def test_voxel_slab(self):
        """
        Test workflow for voxel_slab.
        """

        self._test_workflow("voxel_slab")

    def test_voxel_transformer(self):
        """
        Test workflow for voxel_transformer.
        """

        self._test_workflow("voxel_transformer")


if __name__ == "__main__":
    unittest.main()
