#!/bin/bash
# User script for plotting the solution of a FFT-PEEC problem.
#
# Thomas Guillod
# (c) 2023 - Dartmouth College

set -o nounset
set -o pipefail

# get config
source examples_config.sh

# get the filenames
FILE_SOLUTION="$PATH_ROOT/$FOLDER_NAME/$EXAMPLE_NAME/solution.pck"
FILE_POINT="$PATH_ROOT/$FOLDER_NAME/$EXAMPLE_NAME/point.yaml"
FILE_CONFIG="$PATH_ROOT/$CFG_PYPEEC/configuration.yaml"
FILE_PLOTTER="$PATH_ROOT/$CFG_PLOT/plotter.json"

# run
pypeec --config $FILE_CONFIG plotter \
    --solution $FILE_SOLUTION \
    --point $FILE_POINT \
    --plotter $FILE_PLOTTER
