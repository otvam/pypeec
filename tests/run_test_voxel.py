"""
Test the example with the voxel mesher.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

from tests import test_workflow

# example folder to be tested
folder = "examples_voxel"

# name of the examples
name_list = [
    "voxel_slab",
    "voxel_transformer",
    "voxel_core",
    "voxel_logo",
]

# get the test object
obj = test_workflow.set_init()

# add the tests
for name in name_list:
    test_workflow.set_test(obj, folder, name)
