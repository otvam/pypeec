"""
Test the example with the voxel mesher.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

from tests.code import test_workflow


# duplicate of the test class
class TestVoxel(test_workflow.TestWorkflow):
    pass


# name of the examples
name_list = [
    "examples_voxel/slab",
    "examples_voxel/core",
    "examples_voxel/transformer",
    "examples_voxel/anisotropic",
    "examples_voxel/distributed",
    "examples_voxel/logo",
]

# add the tests
for name in name_list:
    test_workflow.set_test(TestVoxel, name, name, False)
