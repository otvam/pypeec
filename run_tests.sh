#!/bin/bash
# Script for running the tests:
#   - run the tests
#   - check the test status
#
# The variable "ALLOW_PLOTTING" are allowing the tests to be run without a display server.
# The variables "PYTHONIOENCODING" and "PYTHONUNBUFFERED" are setting up Python.
#
# Thomas Guillod - Dartmouth College
# Mozilla Public License Version 2.0

set -o nounset
set -o pipefail

function test_run {
  echo "======================================================================"
  echo "TEST: $1"
  echo "======================================================================"

  python -W ignore:DeprecationWarning -m unittest "tests/$1.py" -v
  ret=$(( ret || $? ))
}

function test_collect {
  echo "======================================================================"
  echo "TEST: SUMMARY"
  echo "======================================================================"
  if [[ $ret == 0 ]]
  then
    echo "SUCCESS"
  else
    echo "FAILURE"
  fi
}

# global variables
export ALLOW_PLOTTING="true"
export PYTHONIOENCODING="utf8"
export PYTHONUNBUFFERED="1"

# init status
ret=0

# run test
test_run test_tutorial
test_run test_voxel
test_run test_shape
test_run test_png
test_run test_stl

# collect results
test_collect

exit $ret
