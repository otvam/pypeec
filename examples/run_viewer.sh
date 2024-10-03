#!/bin/bash
# User script for visualizing a 3D voxel structure.
#
# Thomas Guillod - Dartmouth College
# Mozilla Public License Version 2.0

set -o nounset
set -o pipefail

# get config
source examples_config.sh

# get the filenames
FILE_VOXEL="$PATH_ROOT/$FOLDER_EXAMPLE/voxel.json.gz"
FILE_VIEWER="$PATH_ROOT/$FOLDER_CONFIG/viewer.yaml"

# plot tag (from viewer.yaml)
TAG_PLOT="domain graph"

# run
pypeec viewer \
    --voxel $FILE_VOXEL \
    --viewer $FILE_VIEWER \
    --tag_plot $TAG_PLOT \
    --plot_mode qt
