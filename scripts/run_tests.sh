#!/bin/bash
# Script for running and checking the tests.
#
# Thomas Guillod - Dartmouth College
# Mozilla Public License Version 2.0

set -o nounset
set -o pipefail

function test_run {
  echo "======================================================================"
  echo "TEST: $1"
  echo "======================================================================"

  python -m unittest "tests/$1.py" -v
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

# set up the Python interpreter
export ALLOW_PLOTTING="true"      # tests can run without a display server
export PYTHONIOENCODING="utf8"    # set encoding for the console
export PYTHONUNBUFFERED="1"       # disable buffering for the console

# options for the tests
export TEST_TOL="1e-4"            # relative tolerance for the test results
export TEST_CHECK="1"             # check (or not) the test results
export TEST_SET="0"               # generate (or not) the test results

# change to root directory
cd "$(dirname "$0")" && cd ..

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
