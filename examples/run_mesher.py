"""
User script for meshing a voxel structure.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import os.path
import pypeec
import examples_config

# get the path of the root of the code
PATH_ROOT = os.path.dirname(__file__)

# get config
FOLDER_CONFIG = examples_config.FOLDER_CONFIG
FOLDER_EXAMPLE = examples_config.FOLDER_EXAMPLE


if __name__ == "__main__":
    # get the filenames
    file_geometry = os.path.join(PATH_ROOT, FOLDER_EXAMPLE, "geometry.yaml")
    file_voxel = os.path.join(PATH_ROOT, FOLDER_EXAMPLE, "voxel.json.gz")

    # run
    pypeec.run_mesher_file(
        file_geometry=file_geometry,
        file_voxel=file_voxel,
    )
