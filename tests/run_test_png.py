"""
Test the example with the PNG mesher.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

from tests import test_workflow

# example folder to be tested
folder = "examples_png"

# name of the examples
name_list = [
    "png_inductor_spiral",
    "png_inductor_gap",
    "png_shield",
    "png_busbar",
    "png_gerber",
    "png_wire",
    "png_trace",
]

# get the test object
obj = test_workflow.TestWorkflow

# add the tests
for name in name_list:
    test_workflow.set_test(folder, name)
