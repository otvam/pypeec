#!/bin/bash
# User script for solving a problem with the FFT-PEEC solver.
#
# Thomas Guillod
# (c) 2023 - Dartmouth College

set -o nounset
set -o pipefail

# get config
source examples_config.sh

# get the filename
FILE_PROBLEM="$PATH_ROOT/$EXAMPLE_NAME/problem.json"
FILE_VOXEL="$PATH_ROOT/$EXAMPLE_NAME/voxel.pck"
FILE_SOLUTION="$PATH_ROOT/$EXAMPLE_NAME/solution.pck"

# run
ppsolver --voxel $FILE_VOXEL --problem $FILE_PROBLEM --solution $FILE_SOLUTION