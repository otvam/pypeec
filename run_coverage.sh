#!/bin/bash
# Script for checking the code coverage:
#   - run the tests with coverage analysis
#   - generate an HTML report with the results
#
# The variable "ALLOW_PLOTTING" are allowing the tests to be run without a display server.
# The variables "PYTHONIOENCODING" and "PYTHONUNBUFFERED" are setting up Python.
#
# Thomas Guillod - Dartmouth College
# Mozilla Public License Version 2.0

set -o nounset
set -o pipefail

function coverage_run {
  echo "======================================================================"
  echo "COVERAGE: RUN"
  echo "======================================================================"

  python -W ignore:DeprecationWarning \
      -m coverage run --data-file="coverage/coverage.dat" \
      -m unittest discover tests -v

  ret=$(( ret || $? ))
}

function coverage_html {
  echo "======================================================================"
  echo "COVERAGE: REPORT"
  echo "======================================================================"

  python -W ignore:DeprecationWarning \
      -m coverage html --data-file="coverage/coverage.dat" \
      --title="PyPEEC Coverage Report" \
      --directory="coverage" --quiet

  ret=$(( ret || $? ))

  python -W ignore:DeprecationWarning \
      -m coverage report --data-file="coverage/coverage.dat"

  ret=$(( ret || $? ))
}

# global variables
export ALLOW_PLOTTING="true"
export PYTHONIOENCODING="utf8"
export PYTHONUNBUFFERED="1"

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
