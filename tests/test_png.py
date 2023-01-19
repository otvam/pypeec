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

    def test_png_inductor(self):
        """
        Test workflow for png_inductor.
        """

        test_workflow.test_workflow(self, "png_inductor")

    def test_png_busbar(self):
        """
        Test workflow for png_busbar.
        """

        test_workflow.test_workflow(self, "png_busbar")

    def test_png_wire(self):
        """
        Test workflow for png_wire.
        """

        test_workflow.test_workflow(self, "png_wire")


if __name__ == "__main__":
    unittest.main()
