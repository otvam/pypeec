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

  # clean
  rm -rf dist
  rm -rf build
  rm -rf pypeec.egg-info
  rm -rf pypeec/data/examples.zip
  rm -rf pypeec/data/documentation.zip
  rm -rf pypeec/data/version.txt

  # pack examples
  (cd examples && git archive -o ../pypeec/data/examples.zip HEAD)

  # pack documentation
  (cd html && zip -qr ../pypeec/data/documentation.zip .)

  # build package
  python -m build

  # update status
  ret=$(( ret || $? ))
}

# init status
ret=0

# build the documentation
build_package

exit $ret
