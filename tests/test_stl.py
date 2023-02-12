"""
Test the example with the STL mesher.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import unittest
from tests import test_workflow


class TestMesherViewer(unittest.TestCase):
    """
    Test the workflow different examples.
    """

    def test_stl_inductor_air(self):
        """
        Test workflow for stl_inductor_air.
        """

        res = {
            "n_total_ref": 94424, "n_used_ref": 25152,
            "P_tot_ref": 4.36292496e-03, "W_tot_ref": 7.40771010e-09, "tol": 1e-4,
        }
        test_workflow.test_workflow(self, "stl_inductor_air", res)

    def test_stl_inductor_core(self):
        """
        Test workflow for stl_inductor_core.
        """

        res = {
            "n_total_ref": 161280, "n_used_ref": 33523,
            "P_tot_ref": 3.61488966e-03, "W_tot_ref": 3.70787888e-08, "tol": 1e-4,
        }
        test_workflow.test_workflow(self, "stl_inductor_core", res)

    def test_stl_transformer(self):
        """
        Test workflow for stl_transformer.
        """

        res = {
            "n_total_ref": 102510, "n_used_ref": 23480,
            "P_tot_ref": 1.47073968e-03, "W_tot_ref": 6.07217219e-08, "tol": 1e-4,
        }
        test_workflow.test_workflow(self, "stl_transformer", res)


if __name__ == "__main__":
    unittest.main()
