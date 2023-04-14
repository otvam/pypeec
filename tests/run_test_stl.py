"""
Test the example with the STL mesher.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

from tests import test_workflow

# example folder to be tested
folder = "examples_stl"

# name of the examples
name_list = [
    "stl_inductor_air",
    "stl_inductor_core",
    "stl_transformer",
]

# get the test object
obj = test_workflow.TestWorkflow

# add the tests
for name in name_list:
    test_workflow.set_test(folder, name)