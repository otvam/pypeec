#!/bin/bash
# Script for copying the examples data to the tests and running the tests.
#
# Thomas Guillod
# (c) 2023 - Dartmouth College

function copy_folder {
  folder=$1
  for tmp in "${folder[@]}"
  do
    rm -rf tests/$tmp
    rsync -ma --include '*/' --include '*.json' --exclude '*' examples/$tmp tests
    rsync -ma --include '*/' --include '*.png' --exclude '*' examples/$tmp tests
    rsync -ma --include '*/' --include '*.stl' --exclude '*' examples/$tmp tests
  done
}

function clean_folder {
  folder=$1
  for tmp in "${folder[@]}"
  do
    rm -rf tests/$tmp
  done
}

folder=(
  "visualization"
  "voxel_slab"
  "voxel_transformer"
  "png_wire"
  "png_inductor"
  "stl_inductor"
  "stl_transformer"
)

echo "================================================================"
echo "COPY THE FILES"
echo "================================================================"

copy_folder $folder

echo "================================================================"
echo "RUN THE TESTS"
echo "================================================================"

python -m unittest -v

echo "================================================================"
echo "CLEAN THE FILES"
echo "================================================================"

clean_folder $folder

exit 0




