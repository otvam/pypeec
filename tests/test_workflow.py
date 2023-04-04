"""
Integration test for the complete workflow.
True unit tests are not implemented.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import json
import os.path
import pickle
import tempfile
import logging
import unittest
from pypeec import main

# disable logging to prevent clutter during test evaluation
logging.disable(logging.INFO)

# get the path the folder
path_root = os.path.dirname(__file__)


class TestWorkflow(unittest.TestCase):
    """
    Run the complete workflow.
    """

    def _run_workflow(self, folder, name):
        """
        Run the complete workflow:
            - run the mesher
            - run the viewer
            - run the solver
            - run the plotter

        The intermediate file are stored with temporary files.
        """

        # start the test
        print("run")

        # get input file name
        file_geometry = os.path.join(path_root, "..", "examples", folder, name, "geometry.yaml")
        file_point = os.path.join(path_root, "..", "examples", folder, name, "point.yaml")
        file_problem = os.path.join(path_root, "..", "examples", folder, name, "problem.yaml")

        # get config file name
        file_plotter = os.path.join(path_root, "..", "examples", "config", "plotter.json")
        file_viewer = os.path.join(path_root, "..", "examples", "config", "viewer.json")
        file_tolerance = os.path.join(path_root, "..", "examples", "config", "tolerance.json")

        # get the temporary files
        fid_voxel = tempfile.NamedTemporaryFile(suffix=".pck")
        fid_solution = tempfile.NamedTemporaryFile(suffix=".pck")
        file_voxel = fid_voxel.name
        file_solution = fid_solution.name

        # run the code
        try:
            # run the mesher
            (status, ex) = main.run_mesher(file_geometry, file_voxel)
            self.assertTrue(status, msg="mesher failure : " + str(ex))

            # load the voxel file
            with open(file_voxel, "rb") as fid:
                data_voxel = pickle.load(fid)

            # run the viewer
            (status, ex) = main.run_viewer(file_voxel, file_point, file_viewer, is_silent=True)
            self.assertTrue(status, msg="viewer failure : " + str(ex))

            # run the solver
            (status, ex) = main.run_solver(file_voxel, file_problem, file_tolerance, file_solution)
            self.assertTrue(status, msg="solver failure : " + str(ex))

            # run the plotter
            (status, ex) = main.run_plotter(file_solution, file_point, file_plotter, is_silent=True)
            self.assertTrue(status, msg="plotter failure : " + str(ex))

            # check the solution file
            with open(file_solution, "rb") as fid:
                data_solution = pickle.load(fid)
        finally:
            # close the temporary files
            fid_voxel.close()
            fid_solution.close()

        return data_voxel, data_solution

    def _check_results(self, res, data_voxel, data_solution):
        """
        Check the results produced by the workflow.
        """

        # get the results
        n_total_ref = res["n_total_ref"]
        n_used_ref = res["n_used_ref"]
        P_tot_ref = res["P_tot_ref"]
        W_tot_ref = res["W_tot_ref"]
        tol = res["tol"]

        # check type
        self.assertIsInstance(data_voxel, dict, msg="invalid voxel file")
        self.assertIsInstance(data_solution, dict, msg="invalid solution file")

        # extract the solution
        n_total = data_voxel["voxel_status"]["n_total"]
        n_used = data_voxel["voxel_status"]["n_used"]
        has_converged = data_solution["has_converged"]
        P_tot = data_solution["integral"]["P_tot"]
        W_tot = data_solution["integral"]["W_tot"]

        # check solution
        self.assertEqual(n_total, n_total_ref, msg="invalid number of voxels (complete grid)")
        self.assertEqual(n_used, n_used_ref, msg="invalid number of voxels (non-empty voxels)")
        self.assertTrue(has_converged, msg="solver convergence issue")
        self.assertAlmostEqual(P_tot, P_tot_ref, delta=tol*P_tot_ref, msg="invalid losses")
        self.assertAlmostEqual(W_tot, W_tot_ref, delta=tol*W_tot_ref, msg="invalid energy")

    def run_test(self, folder, name, res):
        """
        Run the workflow and check the results.
        """

        # generate the results
        (data_voxel, data_solution) = self._run_workflow(folder, name)

        # check the results
        self._check_results(res, data_voxel, data_solution)


def set_test(folder, name):
    """
    Add a test case to the test class.
    """

    # file containing the test results
    file_res = os.path.join(path_root, folder, name + ".json")

    # load the test results
    with open(file_res, "r") as fid:
        res = json.load(fid)

    # function describing the test
    def get(self):
        return TestWorkflow.run_test(self, folder, name, res)

    # dynamically add the method as an attribute
    setattr(TestWorkflow, "test_" + name, get)
