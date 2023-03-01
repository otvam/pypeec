#!/bin/bash
# User script for meshing a voxel structure.
#
# Thomas Guillod
# (c) 2023 - Dartmouth College

set -o nounset
set -o pipefail

# get config
source examples_config.sh

# get the filenames
FILE_MESHER="$PATH_ROOT/$EXAMPLE_NAME/mesher.yaml"
FILE_VOXEL="$PATH_ROOT/$EXAMPLE_NAME/voxel.pck"

# run
pypeec mesher --mesher $FILE_MESHER --voxel $FILE_VOXEL
