#!/bin/bash
# Script for building the Python package:
#
# Thomas Guillod - Dartmouth College
# Mozilla Public License Version 2.0

set -o nounset
set -o pipefail

function build_package {
  echo "======================================================================"
  echo "BUILD PACKAGE"
  echo "======================================================================"

  rm -rf dist
  rm -rf pypeec/examples
  git archive -o pypeec/examples.zip HEAD:examples
  python -m build
  status=$(( status || $? ))
}

# init status
status=0

# build the documentation
build_package

exit $status
