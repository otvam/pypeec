#!/bin/sh
# User script for visualizing a 3D voxel structure.
#
# Thomas Guillod - Dartmouth College
# Mozilla Public License Version 2.0

# get the path
PATH_ROOT=$(dirname "$0")

# get config
. "$PATH_ROOT/examples_config.sh"

# get the filenames
FILE_VOXEL="$PATH_ROOT/$FOLDER_EXAMPLE/voxel.json.gz"
FILE_VIEWER="$PATH_ROOT/$FOLDER_CONFIG/viewer.yaml"

# list of plots to be shown (defined in viewer.yaml)
TAG_PLOT="domain graph"

# method used for rendering the plots
PLOT_MODE="qt"

# run
pypeec viewer \
    --voxel $FILE_VOXEL \
    --viewer $FILE_VIEWER \
    --tag_plot $TAG_PLOT \
    --plot_mode $PLOT_MODE
