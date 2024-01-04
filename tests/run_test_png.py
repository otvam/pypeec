"""
Test the example with the PNG mesher.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

from tests.code import test_workflow
from pypeec import main

# name of the examples
name_list = [
    "examples_png/inductor_spiral",
    "examples_png/inductor_gap",
    "examples_png/shield",
    "examples_png/gerber",
]

# show the logo
main.run_hide_logo()

# get the test object
obj = test_workflow.set_init()

# add the tests
for name in name_list:
    test_workflow.set_test(obj, name)
