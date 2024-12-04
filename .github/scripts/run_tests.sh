#!/bin/bash
# Script for running and checking the tests.
#
# Thomas Guillod - Dartmouth College
# Mozilla Public License Version 2.0

set -e
set -u

# set up the Python interpreter
export ALLOW_PLOTTING="true"      # tests can run without a display server
export PYTHONIOENCODING="utf8"    # set encoding for the console
export PYTHONUNBUFFERED="1"       # disable buffering for the console

# options for the tests
export TEST_TOL="1e-4"            # relative tolerance for the test results
export TEST_CHECK="1"             # check (or not) the test results
export TEST_SET="0"               # generate (or not) the test results

# run test
python -m unittest discover tests -v
