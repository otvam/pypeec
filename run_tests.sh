#!/bin/bash
# Script for running the tests:
#   - run the tests
#   - check the test status
#
# Thomas Guillod - Dartmouth College
# Mozilla Public License Version 2.0

set -o nounset
set -o pipefail

function test_run {
  echo "======================================================================"
  echo "TEST: $1"
  echo "======================================================================"

  python -m unittest -v "tests/$1.py"
  ret=$(( ret || $? ))
}

function test_collect {
  echo "======================================================================"
  if (( ret == 0 ))
  then
    echo "TEST: SUCCESS"
  else
    echo "TEST: FAILURE"
  fi
  echo "======================================================================"
}

# init status
ret=0

# run test
test_run run_test_voxel
test_run run_test_shape
test_run run_test_png
test_run run_test_stl

# collect results
test_collect

exit $ret
