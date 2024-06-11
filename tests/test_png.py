"""
Test the example with the PNG mesher.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

from tests.code import test_workflow


# duplicate of the test class
class TestPng(test_workflow.TestWorkflow):
    pass


# name of the examples
name_list = [
    "examples_png/inductor_spiral",
    "examples_png/inductor_gap",
    "examples_png/inductor_pot",
    "examples_png/iron_core",
    "examples_png/shield",
    "examples_png/gerber",
]

# add the tests
for name in name_list:
    test_workflow.set_test(TestPng, name, name, False)
