"""
Configuration for the examples.
Defined with global variables.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import os.path

# get the path of the root of the code
PATH_ROOT = os.path.dirname(__file__)

# name of configuration folder
FOLDER_CONFIG = "config"

# name of the different examples
#   tutorial
#   examples_voxel
#       examples_voxel/slab
#       examples_voxel/core
#       examples_voxel/transformer
#       examples_voxel/anisotropic
#       examples_voxel/distributed
#       examples_voxel/logo
#   examples_shape
#       examples_shape/busbar
#       examples_shape/wire
#       examples_shape/trace
#       examples_shape/coplanar
#   examples_stl
#       examples_stl/inductor_air
#       examples_stl/inductor_core
#       examples_stl/transformer
#   examples_png
#       examples_png/inductor_spiral
#       examples_png/inductor_gap
#       examples_png/iron_core
#       examples_png/shield
#       examples_png/gerber

# name of the selected example
FOLDER_EXAMPLE = "tutorial"
