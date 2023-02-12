"""
Test the example with the voxel mesher.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

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
            "n_total_ref": 40, "n_used_ref": 40,
            "P_tot_ref": 3.51512844e-05, "W_tot_ref": 6.98984100e-09, "tol": 1e-4,
        }
        test_workflow.test_workflow(self, "voxel_slab", res)

    def test_voxel_core(self):
        """
        Test workflow for voxel_core.
        """

        res = {
            "n_total_ref": 125, "n_used_ref": 20,
            "P_tot_ref": 2.00000000e-04, "W_tot_ref": 1.43419494e-08, "tol": 1e-4,
        }
        test_workflow.test_workflow(self, "voxel_core", res)

    def test_voxel_transformer(self):
        """
        Test workflow for voxel_transformer.
        """

        res = {
            "n_total_ref": 75, "n_used_ref": 31,
            "P_tot_ref": 4.59670260e-04, "W_tot_ref": 1.98280381e-09, "tol": 1e-4,
        }
        test_workflow.test_workflow(self, "voxel_transformer", res)


if __name__ == "__main__":
    unittest.main()
