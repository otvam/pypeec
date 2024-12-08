#!/bin/sh
# User script for meshing a voxel structure.
#
# Thomas Guillod - Dartmouth College
# Mozilla Public License Version 2.0

# get the path
PATH_ROOT=$(dirname "$0")

# get config
. "$PATH_ROOT/examples_config.sh"

# get the filenames
FILE_GEOMETRY="$PATH_ROOT/$FOLDER_EXAMPLE/geometry.yaml"
FILE_VOXEL="$PATH_ROOT/$FOLDER_EXAMPLE/voxel.json.gz"

# run
pypeec mesher \
    --geometry $FILE_GEOMETRY \
    --voxel $FILE_VOXEL
