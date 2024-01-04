"""
Test the example with the shape mesher.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

from tests.code import test_workflow
from pypeec import main

# name of the examples
name_list = [
    "examples_shape/busbar",
    "examples_shape/wire",
    "examples_shape/trace",
    "examples_shape/coplanar",
]

# show the logo
main.run_hide_logo()

# get the test object
obj = test_workflow.set_init()

# add the tests
for name in name_list:
    test_workflow.set_test(obj, name)
