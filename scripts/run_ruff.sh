#!/bin/bash
# Script for running the code quality checks (using "ruff").
#
# Thomas Guillod - Dartmouth College
# Mozilla Public License Version 2.0

set -o nounset
set -o pipefail

function ruff_check {
  echo "======================================================================"
  echo "RUFF: CHECK"
  echo "======================================================================"

  ruff check --no-cache .

  ret=$(( ret || $? ))
}

function ruff_format {
  echo "======================================================================"
  echo "RUFF: FORMAT"
  echo "======================================================================"

  ruff format --no-cache --check .

  ret=$(( ret || $? ))
}

function test_collect {
  echo "======================================================================"
  echo "RUFF: SUMMARY"
  echo "======================================================================"
  if [[ $ret == 0 ]]
  then
    echo "SUCCESS"
  else
    echo "FAILURE"
  fi
}

# change to root directory
cd "$(dirname "$0")" && cd ..

# init status
ret=0

# clean coverage
rm -rf coverage
mkdir coverage

# run check
ruff_check

# run format
ruff_format

# collect results
test_collect

exit $ret
