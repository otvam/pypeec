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
  ret=$(( ret || $? ))
}

# init status
ret=0

# build the documentation
build_docs

exit $ret
