#!/bin/bash
# Script for running the tests:
#   - copy the data
#   - run the tests
#   - clean the data
#   - check the test status
#
# Thomas Guillod
# (c) 2023 - Dartmouth College

set -o nounset
set -o pipefail

function init_test {
  echo "================================================================"
  echo "COPY THE FILES"
  echo "================================================================"

  for tmp in "${folder[@]}"
  do
    rm -rf "tests/$tmp"
    rsync -ma --include '*/' --include '*.json' --exclude '*' "examples/$tmp" "tests"
    rsync -ma --include '*/' --include '*.png' --exclude '*' "examples/$tmp" "tests"
    rsync -ma --include '*/' --include '*.stl' --exclude '*' "examples/$tmp" "tests"
  done

  status=0
}

function test_file {
  echo "================================================================"
  echo "TEST: $1"
  echo "================================================================"

  python -m unittest -v "tests/$1.py"
  status=$(( status || $? ))
}

function clean_test {
  echo "================================================================"
  echo "CLEAN THE FILES"
  echo "================================================================"

  for tmp in "${folder[@]}"
  do
    rm -rf "tests/$tmp"
  done

  echo "================================================================"
  if (( status == 0 ))
  then
    echo "TEST: SUCCESS"
  else
    echo "TEST: FAILURE"
  fi
  echo "================================================================"
}

folder=(
  "visualization"
  "voxel_slab"
  "voxel_transformer"
  "png_busbar"
  "png_wire"
  "png_inductor"
  "stl_inductor"
  "stl_transformer"
)

init_test
test_file test_voxel
test_file test_png
test_file test_stl
clean_test

exit 0
