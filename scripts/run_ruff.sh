#!/bin/bash
# Script for running the code quality checks (using "ruff").
#
# Thomas Guillod - Dartmouth College
# Mozilla Public License Version 2.0

set -o nounset
set -o pipefail

function ruff_check {
  echo "======================================================================"
  echo "============================== RUFF: CHECK"
  echo "======================================================================"

  ruff check --no-cache .

  ret=$(( ret || $? ))
}

function ruff_format {
  echo "======================================================================"
  echo "============================== RUFF: FORMAT"
  echo "======================================================================"

  ruff format --no-cache --check .

  ret=$(( ret || $? ))
}

function ret_collect {
  if [[ $ret == 0 ]]
  then
    status="SUCCESS"
  else
    status="FAILURE"
  fi

  echo "======================================================================"
  echo "============================== RUFF: $status"
  echo "======================================================================"
}

# change to root directory
cd "$(dirname "$0")" && cd ..

# init status
ret=0

# run check
ruff_check

# run format
ruff_format

# collect status
ret_collect

exit $ret
