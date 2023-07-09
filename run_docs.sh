#!/bin/bash
# Script for building the Sphinx documentation:
#
# Thomas Guillod - Dartmouth College
# Mozilla Public License Version 2.0

set -o nounset
set -o pipefail

function build_docs {
  echo "======================================================================"
  echo "BUILD DOCUMENTATION"
  echo "======================================================================"

  rm -rf html
  sphinx-build -b html docs html
  status=$(( status || $? ))
}

# init status
status=0

# build the documentation
build_docs

exit $status
