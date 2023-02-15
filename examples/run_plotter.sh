#!/bin/bash
# User script for plotting the solution of a FFT-PEEC problem.
#
# Thomas Guillod
# (c) 2023 - Dartmouth College

set -o nounset
set -o pipefail

# get config
source examples_config.sh

# get the filename
FILE_SOLUTION="$PATH_ROOT/$EXAMPLE_NAME/solution.pck"
FILE_POINT="$PATH_ROOT/$EXAMPLE_NAME/point.yaml"
FILE_PLOTTER="$PATH_ROOT/config/data_plotter.json"

# run
ppplotter --solution $FILE_SOLUTION --point $FILE_POINT --plotter $FILE_PLOTTER
