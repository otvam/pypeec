"""
Test the example with the STL mesher.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

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
            "P_tot_ref": 2.20095306e-03, "W_tot_ref": 9.03438792e-09, "tol": 1e-4,
        }
        test_workflow.test_workflow(self, "stl_inductor_air", res)

    def test_stl_inductor_core(self):
        """
        Test workflow for stl_inductor_core.
        """

        res = {
            "n_total_ref": 161280, "n_used_ref": 33523,
            "P_tot_ref": 2.06078810e-03, "W_tot_ref": 3.85162524e-08, "tol": 1e-4,
        }
        test_workflow.test_workflow(self, "stl_inductor_core", res)

    def test_stl_transformer(self):
        """
        Test workflow for stl_transformer.
        """

        res = {
            "n_total_ref": 102510, "n_used_ref": 23480,
            "P_tot_ref": 1.47073968e-03, "W_tot_ref": 3.03608609e-08, "tol": 1e-4,
        }
        test_workflow.test_workflow(self, "stl_transformer", res)


if __name__ == "__main__":
    unittest.main()
