#!/bin/sh
# User script for plotting the solution of a FFT-PEEC problem.
#
# Thomas Guillod - Dartmouth College
# Mozilla Public License Version 2.0

# get the path
PATH_ROOT=$(dirname "$0")

# get config
. "$PATH_ROOT/examples_config.sh"

# get the filenames
FILE_SOLUTION="$PATH_ROOT/$FOLDER_EXAMPLE/solution.json.gz"
FILE_PLOTTER="$PATH_ROOT/$FOLDER_CONFIG/plotter.yaml"

# list of plots to be shown (defined in plotter.yaml)
TAG_PLOT="V_c_norm J_c_norm H_p_norm residuum"

# method used for rendering the plots
PLOT_MODE="qt"

# run
pypeec plotter \
    --solution $FILE_SOLUTION \
    --plotter $FILE_PLOTTER \
    --tag_plot $TAG_PLOT \
    --plot_mode $PLOT_MODE
