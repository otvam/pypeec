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

# name of the considered example
#   examples_voxel
#       slab
#       transformer
#       core
#       logo
#   examples_shape
#       busbar
#       wire
#       trace
#       coplanar
#   examples_stl
#       inductor_air
#       inductor_core
#       transformer
#   examples_png
#       inductor_spiral
#       inductor_gap
#       shield
#       gerber
FOLDER_NAME = "examples_voxel"
EXAMPLE_NAME = "core"
