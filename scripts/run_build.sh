#!/bin/bash
# Script for building the Python package:
#   - clean the generated files
#   - build the documentation
#   - build the package
#
# Thomas Guillod - Dartmouth College
# Mozilla Public License Version 2.0

set -o nounset
set -o pipefail

function clean_data {
  echo "======================================================================"
  echo "CLEAN DATA"
  echo "======================================================================"

  # clean package
  rm -rf dist
  rm -rf build
  rm -rf pypeec.egg-info

  # clean generated files
  rm -rf pypeec/data/examples.zip
  rm -rf pypeec/data/documentation.zip
  rm -rf pypeec/data/version.txt

  # clean documentation
  rm -rf html
  rm -rf docs/_static
  rm -rf docs/_templates
}

function build_docs {
  echo "======================================================================"
  echo "BUILD DOCUMENTATION"
  echo "======================================================================"

  # create folders
  mkdir docs/_static
  mkdir docs/_templates
  mkdir html

  # build documentation
  sphinx-build -b html docs html

  # update status
  ret=$(( ret || $? ))

  # check external links
  sphinx-build -b linkcheck docs html

  # update status
  ret=$(( ret || $? ))

  # clean data
  rm -rf html/.buildinfo
  rm -rf html/.doctrees
  rm -rf html/output.json
  rm -rf html/output.txt
}

function build_package {
  echo "======================================================================"
  echo "BUILD PACKAGE"
  echo "======================================================================"

  # pack examples
  (cd examples && git archive -o ../pypeec/data/examples.zip HEAD)

  # pack documentation
  (cd html && zip -qr ../pypeec/data/documentation.zip .)

  # build package
  python -m build

  # update status
  ret=$(( ret || $? ))
}

# change to root directory
cd "$(dirname "$0")" && cd ..

# init status
ret=0

# build the documentation
clean_data
build_docs
build_package

exit $ret
