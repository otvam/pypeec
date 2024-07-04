#!/bin/bash
# Script for checking the code coverage:
#   - run the tests with coverage analysis
#   - generate an HTML report with the results
#
# The variable "ALLOW_PLOTTING" are allowing the tests to be run without a display server.
# The variables "PYTHONIOENCODING" and "PYTHONUNBUFFERED" are setting up the Python interpreter.
#
# The following variables control the tests:
#   - TEST_TOL: relative tolerance for the test results
#   - TEST_CHECK: check (or not) the test results
#   - TEST_SET: generate (or not) the test results
#
# Thomas Guillod - Dartmouth College
# Mozilla Public License Version 2.0

set -o nounset
set -o pipefail

function coverage_run {
  echo "======================================================================"
  echo "COVERAGE: RUN"
  echo "======================================================================"

  python \
      -m coverage run \
      --data-file="coverage/coverage.dat" \
      --module unittest discover tests -v

  ret=$(( ret || $? ))
}

function coverage_html {
  echo "======================================================================"
  echo "COVERAGE: REPORT"
  echo "======================================================================"

  python \
      -m coverage html \
      --data-file="coverage/coverage.dat" \
      --title="PyPEEC Coverage Report" \
      --directory="coverage" --quiet

  ret=$(( ret || $? ))

  python -m coverage report --data-file="coverage/coverage.dat"

  ret=$(( ret || $? ))
}

# global variables for the Python interpreter
export ALLOW_PLOTTING="true"
export PYTHONIOENCODING="utf8"
export PYTHONUNBUFFERED="1"

# global variables for disabling the tests
export TEST_TOL="nan"
export TEST_CHECK="0"
export TEST_SET="0"

# change to root directory
cd "$(dirname "$0")" && cd ..

# init status
ret=0

# clean coverage
rm -rf coverage
mkdir coverage

# run coverage
coverage_run

# run report
coverage_html

exit $ret
