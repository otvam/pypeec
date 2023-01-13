"""
Integration test for the mesher and viewer.
True unit tests are not implemented.

The testing is done with the unittest library.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import os
import unittest
import tempfile
import logging
from PyPEEC import script

# disable logging to prevent clutter during test evaluation
logging.disable(logging.CRITICAL)

# get the path the folder
path_root = os.path.dirname(__file__)


class TestMesherViewer(unittest.TestCase):
    """
    Test mesher/viewer for different cases.
    """

    def _test_mesher_viewer(self, name):
        """
        Test mesher/viewer for a specific test case.
        """

        # get input file name
        file_mesher = os.path.join(path_root, "data_mesher/%s.json" % name)
        file_viewer = os.path.join(path_root, "data_viewer_plotter/data_viewer.json")

        # create the temporary output file
        with tempfile.NamedTemporaryFile(suffix='.pck') as fid_voxel:
            # get the temped file name
            file_voxel = fid_voxel.name

            # run the mesher
            status = script.run_mesher(file_mesher, file_voxel)
            self.assertTrue(status, msg="mesher failure")

            # run the viewer
            status = script.run_viewer(file_voxel, file_viewer, False)
            self.assertTrue(status, msg="viewer failure")

    def test_png_inductor(self):
        """
        Test mesher/viewer for png_inductor.
        """

        self._test_mesher_viewer("png_inductor")

    def test_stl_inductor(self):
        """
        Test mesher/viewer for stl_inductor.
        """

        self._test_mesher_viewer("stl_inductor")

    def test_voxel_slab(self):
        """
        Test mesher/viewer for voxel_slab.
        """

        self._test_mesher_viewer("voxel_slab")

    def test_voxel_transformer(self):
        """
        Test mesher/viewer for voxel_transformer.
        """

        self._test_mesher_viewer("voxel_transformer")


if __name__ == '__main__':
    unittest.main()
