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

    def _check_mesher(self, voxel_status, mesher):
        """
        Check the results produced by the mesher.
        """

        # get the results
        n_total_ref = mesher["n_total"]
        n_used_ref = mesher["n_used"]

        # extract the solution
        n_total = voxel_status["n_total"]
        n_used = voxel_status["n_used"]

        # check solution
        self.assertEqual(n_total, n_total_ref, msg="invalid number of voxels (complete grid)")
        self.assertEqual(n_used, n_used_ref, msg="invalid number of voxels (non-empty voxels)")

    def _check_solver(self, data_run, solver, tol):
        """
        Check the results produced by the solver.
        """

        # get the results
        freq_ref = solver["freq"]
        has_converged_ref = solver["has_converged"]
        P_tot_ref = solver["P_tot"]
        W_tot_ref = solver["W_tot"]

        # extract the solution
        freq = data_run["freq"]
        has_converged = data_run["has_converged"]
        P_tot = data_run["integral"]["P_tot"]
        W_tot = data_run["integral"]["W_tot"]

        # check solution
        self.assertEqual(has_converged, has_converged_ref, msg="invalid convergence")
        self.assertAlmostEqual(freq, freq_ref, delta=tol*freq_ref, msg="invalid frequency")
        self.assertAlmostEqual(P_tot, P_tot_ref, delta=tol*P_tot_ref, msg="invalid losses")
        self.assertAlmostEqual(W_tot, W_tot_ref, delta=tol*W_tot_ref, msg="invalid energy")

    def run_test(self, folder, name, data_test):
        """
        Run the workflow and check the results.
        """

        # generate the results
        (data_voxel, data_solution) = self._run_workflow(folder, name)

        # extract results
        tol = data_test["tol"]
        mesher = data_test["mesher"]
        solver = data_test["solver"]

        # extract data
        voxel_status = data_voxel["voxel_status"]
        data_run = data_solution["data_run"]

        # check the mesher
        self._check_mesher(voxel_status, mesher)

        # check the sweep names
        self.assertEqual(data_run.keys(), solver.keys(), "invalid sweep")

        # check the solver
        for tag in data_run:
            data_run_tmp = data_run[tag]
            solver_tmp = solver[tag]
            self._check_solver(data_run_tmp, solver_tmp, tol)


def set_test(folder, name):
    """
    Add a test case to the test class.
    """

    # file containing the test results
    file_test = os.path.join(path_root, folder, name + ".json")

    # load the test results
    with open(file_test, "r") as fid:
        data_test = json.load(fid)

    # function describing the test
    def get(self):
        return TestWorkflow.run_test(self, folder, name, data_test)

    # dynamically add the method as an attribute
    setattr(TestWorkflow, "test_" + name, get)
