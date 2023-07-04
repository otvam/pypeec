"""
Test the complete workflow (mesher, viewer, solver, and plotter).

True unit tests are not implemented.
Only non-regression integration tests are implemented.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import unittest
from tests import test_pypeec
from tests import test_read_write
from tests import test_generate


class TestWorkflow(unittest.TestCase):
    """
    Run the complete workflow.
    """

    def _check_mesher(self, data_geom, mesher):
        """
        Check the results produced by the mesher.
        """

        # get the results
        n_total_ref = mesher["n_total"]
        n_used_ref = mesher["n_used"]

        # extract the solution
        n_total = data_geom["voxel_status"]["n_total"]
        n_used = data_geom["voxel_status"]["n_used"]

        # check solution
        self.assertEqual(n_total, n_total_ref, msg="invalid number of voxels (complete grid)")
        self.assertEqual(n_used, n_used_ref, msg="invalid number of voxels (non-empty voxels)")

    def _check_solver(self, data_sweep, solver, tol):
        """
        Check the results produced by the solver.
        """

        # get the results
        freq_ref = solver["freq"]
        has_converged_ref = solver["has_converged"]
        P_tot_ref = solver["P_tot"]
        W_tot_ref = solver["W_tot"]

        # extract the solution
        freq = data_sweep["freq"]
        has_converged = data_sweep["has_converged"]
        P_tot = data_sweep["integral"]["P_tot"]
        W_tot = data_sweep["integral"]["W_tot"]

        # check solution
        self.assertEqual(has_converged, has_converged_ref, msg="invalid convergence")
        self.assertAlmostEqual(freq, freq_ref, delta=tol*freq_ref, msg="invalid frequency")
        self.assertAlmostEqual(P_tot, P_tot_ref, delta=tol*P_tot_ref, msg="invalid losses")
        self.assertAlmostEqual(W_tot, W_tot_ref, delta=tol*W_tot_ref, msg="invalid energy")

    def _check_results(self, voxel_status, data_sweep, solver, mesher, tol):
        """
        Check the results.
        """

        # check the mesher
        self._check_mesher(voxel_status, mesher)

        # check the solver sweep names
        self.assertEqual(data_sweep.keys(), solver.keys(), "invalid sweep")

        # check the solver results
        for tag in data_sweep:
            data_sweep_tmp = data_sweep[tag]
            solver_tmp = solver[tag]
            self._check_solver(data_sweep_tmp, solver_tmp, tol)

    def run_test(self, folder, name):
        """
        Run the workflow and check the results.
        """

        # get the test configuration
        (tol, check_test, generate_test) = test_read_write.get_config()

        # generate the results
        (data_voxel, data_solution) = test_pypeec.run_workflow(folder, name)

        # extract the data
        data_geom = data_voxel["data_geom"]
        data_sweep = data_solution["data_sweep"]

        # get the reference results for the tests
        if generate_test:
            # generate the new reference results
            (mesher, solver) = test_generate.generate_results(data_geom, data_sweep)

            # write the reference results
            test_read_write.write_results(folder, name, mesher, solver)
        else:
            # load the stored reference results
            (mesher, solver) = test_read_write.read_results(folder, name)

        # check the results
        if check_test:
            self._check_results(data_geom, data_sweep, solver, mesher, tol)


def set_init():
    """
    Set the configuration file.
    """

    # return the test object
    obj = TestWorkflow

    return obj


def set_test(obj, folder, name):
    """
    Add a test case to the test class.
    """

    # function describing the test
    def get(self):
        return obj.run_test(self, folder, name)

    # dynamically add the method as an attribute
    setattr(obj, "test_" + name, get)
