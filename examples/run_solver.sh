#!/bin/bash
# User script for solving a problem with the FFT-PEEC solver.
#
# Thomas Guillod
# (c) 2023 - Dartmouth College

set -o nounset
set -o pipefail

# get config
source examples_config.sh

# get the filenames
FILE_PROBLEM="$PATH_ROOT/$FOLDER_NAME/$EXAMPLE_NAME/problem.yaml"
FILE_VOXEL="$PATH_ROOT/$FOLDER_NAME/$EXAMPLE_NAME/voxel.pck"
FILE_SOLUTION="$PATH_ROOT/$FOLDER_NAME/$EXAMPLE_NAME/solution.pck"
FILE_CONFIG="$PATH_ROOT/$CFG_PYPEEC/configuration.yaml"
FILE_TOLERANCE="$PATH_ROOT/$CFG_PYPEEC/tolerance.yaml"

# run
pypeec --config $FILE_CONFIG solver \
    --voxel $FILE_VOXEL \
    --problem $FILE_PROBLEM \
    --tolerance $FILE_TOLERANCE \
    --solution $FILE_SOLUTION
