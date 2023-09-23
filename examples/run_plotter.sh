#!/bin/bash
# User script for plotting the solution of a FFT-PEEC problem.
#
# Thomas Guillod - Dartmouth College
# Mozilla Public License Version 2.0

set -o nounset
set -o pipefail

# get config
source examples_config.sh

# get the filenames
FILE_SOLUTION="$PATH_ROOT/$FOLDER_NAME/$EXAMPLE_NAME/solution.pck"
FILE_POINT="$PATH_ROOT/$FOLDER_NAME/$EXAMPLE_NAME/point.yaml"
FILE_PLOTTER="$PATH_ROOT/$FOLDER_CONFIG/plotter.yaml"

# run
pypeec plotter \
    --solution $FILE_SOLUTION \
    --point $FILE_POINT \
    --plotter $FILE_PLOTTER \
    --plot_mode qt
