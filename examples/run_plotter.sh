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
FILE_SOLUTION="$PATH_ROOT/$FOLDER_EXAMPLE/solution.pck"
FILE_POINT="$PATH_ROOT/$FOLDER_EXAMPLE/point.yaml"
FILE_PLOTTER="$PATH_ROOT/$FOLDER_CONFIG/plotter.yaml"

# plot tag (from plotter.yaml)
TAG_PLOT="V_c_abs J_c_norm H_norm residuum"

# run
pypeec plotter \
    --solution $FILE_SOLUTION \
    --point $FILE_POINT \
    --plotter $FILE_PLOTTER \
    --tag_plot $TAG_PLOT \
    --plot_mode qt
