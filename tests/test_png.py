"""
Test the example with the PNG mesher.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import unittest
from tests import test_workflow


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

        super().__init__(method, "examples_png")

    def test_png_shield(self):
        """
        Test workflow for png_shield.
        """

        res = {
            "n_total_ref": 20808, "n_used_ref": 3210,
            "P_tot_ref": 3.71895778e-04, "W_tot_ref": 7.91119490e-09, "tol": 1e-4,
        }
        self._run_test(res)

    def test_png_inductor_spiral(self):
        """
        Test workflow for png_inductor_spiral.
        """

        res = {
            "n_total_ref": 225280, "n_used_ref": 16896,
            "P_tot_ref": 1.55220537e-02, "W_tot_ref": 4.46954969e-09, "tol": 1e-4,
        }
        self._run_test(res)

    def test_png_inductor_gap(self):
        """
        Test workflow for png_inductor_gap.
        """

        res = {
            "n_total_ref": 87480, "n_used_ref": 34196,
            "P_tot_ref": 6.66909878e-05, "W_tot_ref": 3.71206337e-08, "tol": 1e-4,
        }
        self._run_test(res)

    def test_png_busbar(self):
        """
        Test workflow for png_busbar.
        """

        res = {
            "n_total_ref": 9604, "n_used_ref": 3341,
            "P_tot_ref": 2.29063158e-03, "W_tot_ref": 2.15224596e-10, "tol": 1e-4,
        }
        self._run_test(res)

    def test_png_gerber(self):
        """
        Test workflow for png_gerber.
        """

        res = {
            "n_total_ref": 600372, "n_used_ref": 82546,
            "P_tot_ref": 5.61707175e-02, "W_tot_ref": 3.69553507e-09, "tol": 1e-4,
        }
        self._run_test(res)

    def test_png_trace(self):
        """
        Test workflow for png_trace.
        """

        res = {
            "n_total_ref": 58564, "n_used_ref": 1945,
            "P_tot_ref": 7.65291474e-03, "W_tot_ref": 4.67362770e-09, "tol": 1e-4,
        }
        self._run_test(res)

    def test_png_wire(self):
        """
        Test workflow for png_wire.
        """

        res = {
            "n_total_ref": 24010, "n_used_ref": 18770,
            "P_tot_ref": 2.09630131e-05, "W_tot_ref": 3.07737561e-10, "tol": 1e-4,
        }
        self._run_test(res)


if __name__ == "__main__":
    unittest.main()
