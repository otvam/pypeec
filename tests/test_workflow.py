"""
Test the complete workflow (mesher, viewer, solver, and plotter).

True unit tests are not implemented.
Only non-regression integration tests are implemented.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import unittest
from tests import test_data
from tests import test_generate


class TestWorkflow(unittest.TestCase):
    """
    Run the complete workflow.
    """

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

    def _check_results(self, voxel_status, data_run, solver, mesher, tol):
        """
        Check the results.
        """

        # check the mesher
        self._check_mesher(voxel_status, mesher)

        # check the solver sweep names
        self.assertEqual(data_run.keys(), solver.keys(), "invalid sweep")

        # check the solver results
        for tag in data_run:
            data_run_tmp = data_run[tag]
            solver_tmp = solver[tag]
            self._check_solver(data_run_tmp, solver_tmp, tol)

    def run_test(self, folder, name):
        """
        Run the workflow and check the results.
        """

        # get the test configuration
        (tol, check_test, generate_test) = test_data.get_config()

        # generate the results
        (data_voxel, data_solution) = test_data.run_workflow(folder, name)

        # extract data
        voxel_status = data_voxel["voxel_status"]
        data_run = data_solution["data_run"]

        # get the reference results for the tests
        if generate_test:
            # generate the new reference results
            (mesher, solver) = test_generate.generate_results(voxel_status, data_run)

            # write the reference results
            test_data.write_test_results(folder, name, mesher, solver)
        else:
            # load the stored reference results
            (mesher, solver) = test_data.read_test_results(folder, name)

        # check the results
        if check_test:
            self._check_results(voxel_status, data_run, solver, mesher, tol)


def set_test(folder, name):
    """
    Add a test case to the test class.
    """

    # function describing the test
    def get(self):
        return TestWorkflow.run_test(self, folder, name)

    # dynamically add the method as an attribute
    setattr(TestWorkflow, "test_" + name, get)
