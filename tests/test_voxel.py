"""
Test the example with the voxel mesher.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import unittest
from tests import test_workflow


class TestMesherViewer(unittest.TestCase):
    """
    Test the workflow different examples.
    """

    def test_voxel_slab(self):
        """
        Test workflow for voxel_slab.
        """

        res = {
            "n_total_ref": 28, "n_used_ref": 28,
            "P_tot_ref": 7.49997749e-07, "W_tot_ref": 1.78093265e-09, "tol": 1e-4,
        }
        test_workflow.test_workflow(self, "voxel_slab", res)

    def test_voxel_core(self):
        """
        Test workflow for voxel_core.
        """

        res = {
            "n_total_ref": 175, "n_used_ref": 55,
            "P_tot_ref": 5.45468125e-05, "W_tot_ref": 1.03548738e-08, "tol": 1e-4,
        }
        test_workflow.test_workflow(self, "voxel_core", res)

    def test_voxel_transformer(self):
        """
        Test workflow for voxel_transformer.
        """

        res = {
            "n_total_ref": 75, "n_used_ref": 31,
            "P_tot_ref": 4.59670260e-04, "W_tot_ref": 9.91401905e-10, "tol": 1e-4,
        }
        test_workflow.test_workflow(self, "voxel_transformer", res)

    def test_voxel_logo(self):
        """
        Test workflow for voxel_logo.
        """

        res = {
            "n_total_ref": 27, "n_used_ref": 15,
            "P_tot_ref": 3.57142857e-02, "W_tot_ref": 4.41185013e-09, "tol": 1e-4,
        }
        test_workflow.test_workflow(self, "voxel_logo", res)


if __name__ == "__main__":
    unittest.main()
