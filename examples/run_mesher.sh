#!/bin/bash
# User script for meshing a voxel structure.
#
# Thomas Guillod - Dartmouth College
# Mozilla Public License Version 2.0

set -o nounset
set -o pipefail

# get config
source examples_config.sh

# get the filenames
FILE_GEOMETRY="$PATH_ROOT/$FOLDER_EXAMPLE/geometry.yaml"
FILE_VOXEL="$PATH_ROOT/$FOLDER_EXAMPLE/voxel.json.gz"

# run
pypeec mesher \
    --geometry $FILE_GEOMETRY \
    --voxel $FILE_VOXEL
