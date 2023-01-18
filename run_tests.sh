#!/bin/bash
# Script for copying the examples data to the tests and running the tests.
#
# Thomas Guillod
# (c) 2023 - Dartmouth College

function copy_file {
  FOLDER=$1
  NAME=$2

  SRC="examples/${FOLDER}/${NAME}"
  DST="tests/${FOLDER}/${NAME}"
  cp $SRC $DST
}

function copy_folder {
  FOLDER=$1
  NAME=$2

  SRC="examples/${FOLDER}/${NAME}"
  DST="tests/${FOLDER}"
  cp -R $SRC $DST
}

echo "================================================================"
echo "COPY THE FILES"
echo "================================================================"

echo "copy the viewer and plotter configuration files"
copy_file "data_visualization" "data_viewer.json"
copy_file "data_visualization" "data_plotter.json"

echo "copy the mesher files"
copy_file "data_mesher" "png_inductor.json"
copy_file "data_mesher" "stl_inductor.json"
copy_file "data_mesher" "voxel_slab.json"
copy_file "data_mesher" "voxel_transformer.json"
copy_folder "data_mesher" "png_inductor"
copy_folder "data_mesher" "stl_inductor"

echo "copy the point files"
copy_file "data_point" "png_inductor.json"
copy_file "data_point" "stl_inductor.json"
copy_file "data_point" "voxel_slab.json"
copy_file "data_point" "voxel_transformer.json"

echo "copy the problem files"
copy_file "data_problem" "voxel_slab.json"
copy_file "data_problem" "voxel_transformer.json"

echo "copy the voxel files"
copy_file "data_voxel" "voxel_slab.pck"
copy_file "data_voxel" "voxel_transformer.pck"

echo "================================================================"
echo "RUN THE TESTS"
echo "================================================================"

python -m unittest -v

exit 0




