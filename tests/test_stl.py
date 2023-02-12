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

        test_workflow.test_workflow(self, "stl_inductor_air")

    def test_stl_inductor_core(self):
        """
        Test workflow for stl_inductor_core.
        """

        test_workflow.test_workflow(self, "stl_inductor_core")

    def test_stl_transformer(self):
        """
        Test workflow for stl_transformer.
        """

        test_workflow.test_workflow(self, "stl_transformer")


if __name__ == "__main__":
    unittest.main()
