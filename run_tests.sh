#!/bin/bash
# Script for running the tests:
#   - run the tests
#   - check the test status
#
# Thomas Guillod - Dartmouth College
# Mozilla Public License Version 2.0

set -o nounset
set -o pipefail

function test_file {
  echo "======================================================================"
  echo "TEST: $1"
  echo "======================================================================"

  python -m unittest -v "tests/$1.py"
  status=$(( status || $? ))
}

function clean_test {
  echo "======================================================================"
  if (( status == 0 ))
  then
    echo "TEST: SUCCESS"
  else
    echo "TEST: FAILURE"
  fi
  echo "======================================================================"
}

# init status
status=0

# run test
test_file run_test_voxel
test_file run_test_shape
test_file run_test_png
test_file run_test_stl

# collect results
clean_test

exit $status
