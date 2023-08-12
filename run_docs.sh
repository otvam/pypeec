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

  # clean
  rm -rf html
  rm -rf docs/_static
  rm -rf docs/_templates

  # create folders
  mkdir docs/_static
  mkdir docs/_templates

  # build documentation
  sphinx-build -b html docs html

  # update status
  ret=$(( ret || $? ))
}

# init status
ret=0

# build the documentation
build_docs

exit $ret
