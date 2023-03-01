#!/bin/bash
# User script for visualizing a 3D voxel structure.
#
# Thomas Guillod
# (c) 2023 - Dartmouth College

set -o nounset
set -o pipefail

# get config
source examples_config.sh

# get the filenames
FILE_VOXEL="$PATH_ROOT/$EXAMPLE_NAME/voxel.pck"
FILE_POINT="$PATH_ROOT/$EXAMPLE_NAME/point.yaml"
FILE_VIEWER="$PATH_ROOT/config/viewer.json"

# run
pypeec viewer --voxel $FILE_VOXEL --point $FILE_POINT --viewer $FILE_VIEWER
