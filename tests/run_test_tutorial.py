"""
Test the tutorial example.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

from tests.code import test_workflow
from pypeec import main

# name of the tutorial
name = "tutorial"

# show the logo
main.run_hide_logo()

# get the test object
obj = test_workflow.set_init()

# add the tests
test_workflow.set_test(obj, name)
