"""
Test the example with the shape mesher.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

from tests.code import test_workflow


# duplicate of the test class
class TestShape(test_workflow.TestWorkflow):
    pass


# name of the examples
name_list = [
    "examples_shape/coplanar",
    "examples_shape/parallel",
    "examples_shape/busbar",
    "examples_shape/wire",
    "examples_shape/hole",
    "examples_shape/pwm",
]

# add the tests
for name in name_list:
    test_workflow.set_test(TestShape, name, name, False)
