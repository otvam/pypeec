#!/bin/bash
# User script for visualizing a 3D voxel structure.
#
# Thomas Guillod
# (c) 2023 - Dartmouth College

set -o nounset
set -o pipefail

# get config
source examples_config.sh

# get the filename
FILE_POINT="$PATH_ROOT/$EXAMPLE_NAME/point.json"
FILE_VIEWER="$PATH_ROOT/visualization/data_viewer.json"
FILE_VOXEL="$PATH_ROOT/$EXAMPLE_NAME/voxel.pck"

# run
ppviewer --voxel $FILE_VOXEL --point $FILE_POINT --viewer $FILE_VIEWER
