"""
Configuration for the examples.
Defined with global variables.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import os.path

# get the path of the root of the code
PATH_ROOT = os.path.dirname(__file__)

# name of the considered example
#   voxel_slab
#   voxel_transformer
#   voxel_core
#   stl_inductor_air
#   stl_inductor_core
#   stl_transformer
#   png_inductor_spiral
#   png_inductor_gap
#   png_shield
#   png_busbar
#   png_wire
#   png_pcb
EXAMPLE_NAME = "voxel_core"
