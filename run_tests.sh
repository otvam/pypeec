#!/bin/bash
# Script for running the tests:
#   - copy the data
#   - run the tests
#   - clean the data
#   - check the test status
#
# (c) Thomas Guillod - Dartmouth College

set -o nounset
set -o pipefail

function test_file {
  echo "================================================================"
  echo "TEST: $1"
  echo "================================================================"

  python -W ignore:DeprecationWarning -m unittest -v "tests/$1.py"
  status=$(( status || $? ))
}

function clean_test {
  echo "================================================================"
  if (( status == 0 ))
  then
    echo "TEST: SUCCESS"
  else
    echo "TEST: FAILURE"
  fi
  echo "================================================================"
}

# init status
status=0

# run test
test_file test_voxel
test_file test_png
test_file test_stl

# collect results
clean_test

exit 0
