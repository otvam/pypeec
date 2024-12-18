#!/bin/bash
# Script for running a code coverage analysis (using "coverage").
#
# Thomas Guillod - Dartmouth College
# Mozilla Public License Version 2.0

set -o nounset
set -o pipefail

function coverage_run {
  echo "======================================================================"
  echo "============================== COVERAGE: RUN"
  echo "======================================================================"

  # clean coverage
  rm -rf coverage
  mkdir -p coverage

  # run the coverage report
  python \
      -m coverage run \
      --source="pypeec" \
      --data-file="coverage/coverage.dat" \
      --module unittest discover tests -v

  ret=$(( ret || $? ))
}

function coverage_html {
  echo "======================================================================"
  echo "============================== COVERAGE: REPORT"
  echo "======================================================================"

  # generate the html output
  python \
      -m coverage html \
      --data-file="coverage/coverage.dat" \
      --title="PyPEEC Coverage Report" \
      --directory="coverage" --quiet

  ret=$(( ret || $? ))

  # generate the console output
  python -m coverage report --data-file="coverage/coverage.dat"

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
  echo "============================== COVERAGE: $status"
  echo "======================================================================"
}

# set up the Python interpreter
export ALLOW_PLOTTING="true"      # tests can run without a display server
export PYTHONIOENCODING="utf8"    # set encoding for the console
export PYTHONUNBUFFERED="1"       # disable buffering for the console

# options for the tests
export TEST_TOL="nan"             # relative tolerance for the test results
export TEST_CHECK="0"             # check (or not) the test results
export TEST_SET="0"               # generate (or not) the test results

# change to root directory
cd "$(dirname "$0")" && cd ..

# init status
ret=0

# run coverage
coverage_run

# run report
coverage_html

# collect status
ret_collect

exit $ret
