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

        test_workflow.test_workflow(self, "voxel_slab")

    def test_voxel_transformer(self):
        """
        Test workflow for voxel_transformer.
        """

        test_workflow.test_workflow(self, "voxel_transformer")


if __name__ == "__main__":
    unittest.main()
