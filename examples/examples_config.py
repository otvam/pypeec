"""
Configuration for the examples.
Defined with global variables.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import os.path

# get the path of the root of the code
PATH_ROOT = os.path.dirname(__file__)

# name of config folder
FOLDER_CONFIG = "config"

# name of the considered example
#   examples_voxel
#       voxel_slab
#       voxel_transformer
#       voxel_core
#       voxel_logo
#   examples_shape
#       shape_busbar
#       shape_wire
#       shape_trace
#       shape_coplanar
#   examples_stl
#       stl_inductor_air
#       stl_inductor_core
#       stl_transformer
#   examples_png
#       png_inductor_spiral
#       png_inductor_gap
#       png_shield
#       png_gerber
FOLDER_NAME = "examples_voxel"
EXAMPLE_NAME = "voxel_core"
