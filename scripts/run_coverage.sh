#!/bin/bash
# Script for checking the code coverage.
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

# clean coverage
rm -rf coverage
mkdir coverage

# run coverage
coverage_run

# run report
coverage_html

exit $ret
