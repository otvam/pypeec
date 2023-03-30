"""
Test the example with the STL mesher.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import unittest
from tests import test_workflow


class TestMesherViewer(test_workflow.TestWorkflow):
    """
    Test the workflow for different examples.
    """

    def __init__(self, method):
        """
        Constructor.
        """

        super().__init__(method, "examples_stl")

    def test_stl_inductor_air(self):
        """
        Test workflow for stl_inductor_air.
        """

        res = {
            "n_total_ref": 94424, "n_used_ref": 25152,
            "P_tot_ref": 2.20095306e-03, "W_tot_ref": 9.03438792e-09, "tol": 1e-4,
        }
        self._run_test(res)

    def test_stl_inductor_core(self):
        """
        Test workflow for stl_inductor_core.
        """

        res = {
            "n_total_ref": 161280, "n_used_ref": 33523,
            "P_tot_ref": 2.06078810e-03, "W_tot_ref": 3.85162524e-08, "tol": 1e-4,
        }
        self._run_test(res)

    def test_stl_transformer(self):
        """
        Test workflow for stl_transformer.
        """

        res = {
            "n_total_ref": 102510, "n_used_ref": 23480,
            "P_tot_ref": 1.47073968e-03, "W_tot_ref": 3.03608609e-08, "tol": 1e-4,
        }
        self._run_test(res)


if __name__ == "__main__":
    unittest.main()
