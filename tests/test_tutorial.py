"""
Test the tutorial example.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

from tests.code import test_workflow


# duplicate of the test class
class TestTutorial(test_workflow.TestWorkflow):
    pass


# add the tests
test_workflow.set_test(TestTutorial, "tutorial_api", "tutorial", False)
test_workflow.set_test(TestTutorial, "tutorial_script", "tutorial", True)
