#!/bin/bash
# Script for testing the main script.
#
# Thomas Guillod - Dartmouth College
# Mozilla Public License Version 2.0

set -e
set -u

# set up the Python interpreter
export ALLOW_PLOTTING="true"      # tests can run without a display server
export PYTHONIOENCODING="utf8"    # set encoding for the console
export PYTHONUNBUFFERED="1"       # disable buffering for the console

# check the version
pypeec --version

# extract the data
pypeec examples examples
pypeec documentation documentation

# run the mesher
pypeec mesher \
  --geometry examples/tutorial/geometry.yaml \
  --voxel examples/tutorial/voxel.json.gz

# run the solver
pypeec solver \
  --voxel examples/tutorial/voxel.json.gz \
  --problem examples/tutorial/problem.yaml \
  --tolerance examples/config/tolerance.yaml \
  --solution examples/tutorial/solution.json.gz

# run the viewer
pypeec viewer \
  --voxel examples/tutorial/voxel.json.gz \
  --viewer examples/config/viewer.yaml \
  --plot_mode debug

# run the plotter
pypeec plotter \
  --solution examples/tutorial/solution.json.gz \
  --plotter examples/config/plotter.yaml \
  --plot_mode debug
