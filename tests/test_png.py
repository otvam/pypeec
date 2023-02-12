"""
Test the example with the PNG mesher.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import unittest
from tests import test_workflow


class TestMesherViewer(unittest.TestCase):
    """
    Test the workflow different examples.
    """

    def test_png_shield(self):
        """
        Test workflow for png_shield.
        """

        res = {
            "n_total_ref": 20808, "n_used_ref": 3210,
            "P_tot_ref": 1.85947889e-04, "W_tot_ref": 7.91119313e-09, "tol": 1e-4,
        }
        test_workflow.test_workflow(self, "png_shield", res)

    def test_png_inductor(self):
        """
        Test workflow for png_inductor.
        """

        res = {
            "n_total_ref": 225280, "n_used_ref": 16896,
            "P_tot_ref": 1.55220537e-02, "W_tot_ref": 8.93909937e-09, "tol": 1e-4,
        }
        test_workflow.test_workflow(self, "png_inductor", res)

    def test_png_busbar(self):
        """
        Test workflow for png_busbar.
        """

        res = {
            "n_total_ref": 9604, "n_used_ref": 3341,
            "P_tot_ref": 2.29063158e-03, "W_tot_ref": 4.30449191e-10, "tol": 1e-4,
        }
        test_workflow.test_workflow(self, "png_busbar", res)

    def test_png_pcb(self):
        """
        Test workflow for png_pcb.
        """

        res = {
            "n_total_ref": 58564, "n_used_ref": 1945,
            "P_tot_ref": 3.82645737e-03, "W_tot_ref": 4.67362768e-09, "tol": 1e-4,
        }
        test_workflow.test_workflow(self, "png_pcb", res)

    def test_png_wire(self):
        """
        Test workflow for png_wire.
        """

        res = {
            "n_total_ref": 24010, "n_used_ref": 18770,
            "P_tot_ref": 9.99920463e-05, "W_tot_ref": 4.58137101e-09, "tol": 1e-4,
        }
        test_workflow.test_workflow(self, "png_wire", res)


if __name__ == "__main__":
    unittest.main()
