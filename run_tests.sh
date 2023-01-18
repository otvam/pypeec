#!/bin/bash
# Script for copying the examples data to the tests and running the tests.
#
# Thomas Guillod
# (c) 2023 - Dartmouth College

function copy_folder {
  echo "copy / $1"
  rm -rf tests/$1
  rsync -ma --include '*/' --include '*.json' --exclude '*' examples/$1 tests
  rsync -ma --include '*/' --include '*.png' --exclude '*' examples/$1 tests
  rsync -ma --include '*/' --include '*.stl' --exclude '*' examples/$1 tests
}

echo "================================================================"
echo "COPY THE FILES"
echo "================================================================"

copy_folder visualization
copy_folder voxel_slab
copy_folder voxel_transformer
copy_folder png_cylinder
copy_folder png_inductor
copy_folder stl_inductor
copy_folder stl_transformer

echo "================================================================"
echo "RUN THE TESTS"
echo "================================================================"

python -m unittest -v

exit 0




