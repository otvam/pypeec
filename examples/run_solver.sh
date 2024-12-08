#!/bin/sh
# User script for solving a problem with the FFT-PEEC solver.
#
# Thomas Guillod - Dartmouth College
# Mozilla Public License Version 2.0

# get the path
PATH_ROOT=$(dirname "$0")

# get config
. "$PATH_ROOT/examples_config.sh"

# get the filenames
FILE_PROBLEM="$PATH_ROOT/$FOLDER_EXAMPLE/problem.yaml"
FILE_VOXEL="$PATH_ROOT/$FOLDER_EXAMPLE/voxel.json.gz"
FILE_SOLUTION="$PATH_ROOT/$FOLDER_EXAMPLE/solution.json.gz"
FILE_TOLERANCE="$PATH_ROOT/$FOLDER_CONFIG/tolerance.yaml"

# run
pypeec solver \
    --voxel $FILE_VOXEL \
    --problem $FILE_PROBLEM \
    --tolerance $FILE_TOLERANCE \
    --solution $FILE_SOLUTION
