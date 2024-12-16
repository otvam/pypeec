"""
Test the complete workflow (mesher, viewer, solver, and plotter).

The tests are covering all the main functionalities.
The tests are using the examples and  the tutorial to check the code.
Only integration tests are currently implemented (no unit tests).
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import os
import unittest
from tests.code import test_pypeec
from tests.code import test_read_write
from tests.code import test_generate


class TestWorkflow(unittest.TestCase):
    """
    Run the complete workflow.
    """

    def _check_mesher(self, mesher, mesher_ref):
        """
        Check the results produced by the mesher.
        """

        # get the results
        n_total_ref = mesher_ref["n_total"]
        n_used_ref = mesher_ref["n_used"]

        # extract the solution
        n_total = mesher["n_total"]
        n_used = mesher["n_used"]

        # check solution
        self.assertEqual(n_total, n_total_ref, msg="invalid number of voxels (complete grid)")
        self.assertEqual(n_used, n_used_ref, msg="invalid number of voxels (non-empty voxels)")

    def _check_solver(self, solver, solver_ref, test_tol):
        """
        Check the results produced by the solver.
        """

        # get the results
        freq_ref = solver_ref["freq"]
        has_converged_ref = solver_ref["has_converged"]
        P_total_ref = solver_ref["P_total"]
        W_total_ref = solver_ref["W_total"]

        # extract the solution
        freq = solver["freq"]
        has_converged = solver["has_converged"]
        P_total = solver["P_total"]
        W_total = solver["W_total"]

        # check solution
        self.assertEqual(has_converged, has_converged_ref, msg="invalid convergence")
        self.assertAlmostEqual(freq, freq_ref, delta=test_tol * freq_ref, msg="invalid frequency")
        self.assertAlmostEqual(P_total, P_total_ref, delta=test_tol * P_total_ref, msg="invalid losses")
        self.assertAlmostEqual(W_total, W_total_ref, delta=test_tol * W_total_ref, msg="invalid energy")

    def _check_results(self, mesher, solver, mesher_ref, solver_ref, test_tol):
        """
        Check the results.
        """

        # check the mesher
        self._check_mesher(mesher, mesher_ref)

        # check the solver sweep names
        self.assertEqual(solver.keys(), solver_ref.keys(), "invalid sweep")

        # check the solver results
        for solver_tmp, solver_ref_tmp in zip(solver.values(), solver_ref.values(), strict=True):
            self._check_solver(solver_tmp, solver_ref_tmp, test_tol)

    def run_test(self, tag, name, use_script):
        """
        Run the workflow and check the results.
        """

        # get env var
        test_tol = os.getenv("TEST_TOL")
        test_check = os.getenv("TEST_CHECK")
        test_set = os.getenv("TEST_SET")

        # check env variables
        self.assertIsNotNone(test_tol, "invalid test env variables")
        self.assertIsNotNone(test_check, "invalid test env variables")
        self.assertIsNotNone(test_set, "invalid test env variables")

        # cast env variables
        test_tol = float(test_tol)
        test_check = bool(int(test_check))
        test_set = bool(int(test_set))

        # generate the results
        (data_voxel, data_solution) = test_pypeec.run_workflow(name, use_script)

        # parse the obtained results
        (mesher, solver) = test_generate.generate_results(data_voxel, data_solution)

        # write the reference results
        if test_set:
            test_read_write.write_results(tag, mesher, solver)

        # load and check the results
        if test_check:
            (mesher_ref, solver_ref) = test_read_write.read_results(tag)
            self._check_results(mesher, solver, mesher_ref, solver_ref, test_tol)


def set_test(test_class, tag, name, use_script):
    """
    Add a test case to the test class.
    """

    # function describing the test
    def get(self):
        return test_class.run_test(self, tag, name, use_script)

    # dynamically add the method as an attribute
    setattr(test_class, "test/" + tag, get)
