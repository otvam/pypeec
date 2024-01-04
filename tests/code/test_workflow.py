"""
Test the complete workflow (mesher, viewer, solver, and plotter).

True unit tests are not implemented.
Only non-regression integration tests are implemented.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

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

    def _check_solver(self, solver, solver_ref, tol):
        """
        Check the results produced by the solver.
        """

        # get the results
        freq_ref = solver_ref["freq"]
        has_converged_ref = solver_ref["has_converged"]
        P_tot_ref = solver_ref["P_tot"]
        W_tot_ref = solver_ref["W_tot"]

        # extract the solution
        freq = solver["freq"]
        has_converged = solver["has_converged"]
        P_tot = solver["P_tot"]
        W_tot = solver["W_tot"]

        # check solution
        self.assertEqual(has_converged, has_converged_ref, msg="invalid convergence")
        self.assertAlmostEqual(freq, freq_ref, delta=tol*freq_ref, msg="invalid frequency")
        self.assertAlmostEqual(P_tot, P_tot_ref, delta=tol*P_tot_ref, msg="invalid losses")
        self.assertAlmostEqual(W_tot, W_tot_ref, delta=tol*W_tot_ref, msg="invalid energy")

    def _check_results(self, mesher, solver, mesher_ref, solver_ref, tol):
        """
        Check the results.
        """

        # check the mesher
        self._check_mesher(mesher, mesher_ref)

        # check the solver sweep names
        self.assertEqual(solver.keys(), solver_ref.keys(), "invalid sweep")

        # check the solver results
        for solver_tmp, solver_ref_tmp in zip(solver.values(), solver_ref.values()):
            self._check_solver(solver_tmp, solver_ref_tmp, tol)

    def run_test(self, name):
        """
        Run the workflow and check the results.
        """

        # get the test configuration
        (tol, check_test, generate_test) = test_read_write.get_config()

        # generate the results
        (data_voxel, data_solution) = test_pypeec.run_workflow(name)

        # parse the obtained results
        (mesher, solver) = test_generate.generate_results(data_voxel, data_solution)

        # write the reference results
        if generate_test:
            test_read_write.write_results(name, mesher, solver)

        # load the stored reference results
        (mesher_ref, solver_ref) = test_read_write.read_results(name)

        # check the results
        if check_test:
            self._check_results(mesher, solver, mesher_ref, solver_ref, tol)


def set_init():
    """
    Set the configuration file.
    """

    # return the test object
    obj = TestWorkflow

    return obj


def set_test(obj, name):
    """
    Add a test case to the test class.
    """

    # function describing the test
    def get(self):
        return obj.run_test(self, name)

    # dynamically add the method as an attribute
    setattr(obj, "test/" + name, get)
