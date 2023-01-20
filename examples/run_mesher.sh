#!/bin/bash
# User script for meshing a voxel structure.
#
# Thomas Guillod
# (c) 2023 - Dartmouth College

set -o nounset
set -o pipefail

# get config
source examples_config.sh

# get the filename
FILE_MESHER="$PATH_ROOT/$EXAMPLE_NAME/mesher.json"
FILE_VOXEL="$PATH_ROOT/$EXAMPLE_NAME/voxel.pck"

# run
ppmesher --mesher $FILE_MESHER --voxel $FILE_VOXEL
