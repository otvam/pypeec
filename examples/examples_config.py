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
#   examples_voxel/voxel_slab
#   examples_voxel/voxel_transformer
#   examples_voxel/voxel_core
#   examples_voxel/voxel_logo
#   examples_stl/stl_inductor_air
#   examples_stl/stl_inductor_core
#   examples_stl/stl_transformer
#   examples_png/png_inductor_spiral
#   examples_png/png_inductor_gap
#   examples_png/png_shield
#   examples_png/png_busbar
#   examples_png/png_gerber
#   examples_png/png_wire
#   examples_png/png_trace
# FOLDER_NAME = "examples_shape"
# EXAMPLE_NAME = "shape_busbar"

# FOLDER_NAME = "examples_stl"
# EXAMPLE_NAME = "stl_inductor_air"

FOLDER_NAME = "examples_png"
EXAMPLE_NAME = "png_busbar"
