"""
Test the example with the shape mesher.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

from tests import test_workflow

# example folder to be tested
folder = "examples_shape"

# name of the examples
name_list = [
    "shape_busbar",
    "shape_wire",
    "shape_trace",
]

# get the test object
obj = test_workflow.TestWorkflow

# add the tests
for name in name_list:
    test_workflow.set_test(folder, name)