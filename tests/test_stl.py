"""
Test the example with the STL mesher.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

from tests.code import test_workflow
from pypeec import main


# duplicate of the test class
class TestStl(test_workflow.TestWorkflow):
    pass


# name of the examples
name_list = [
    "examples_stl/inductor_air",
    "examples_stl/inductor_core",
    "examples_stl/transformer",
]

# show the logo
main.run_hide_logo()

# add the tests
for name in name_list:
    test_workflow.set_test(TestStl, name, name, False)
