#!/bin/bash
# Script for creating the development environment:
#   - using Conda for Python and MKL
#   - using Pip for the Python packages
#
# WARNING: Some libraries are hardware/platform/version specific.
#          Therefore, some adaptations might be required for your system.
#
# (c) Thomas Guillod - Dartmouth College

set -o nounset
set -o pipefail

# check argument
if [ "$#" -ne 1 ]; then
    echo "error : usage : run_env.sh CONDA_PATH"
    exit 1
fi

# activate conda
CONDA_PATH="$1/bin/activate"
source $CONDA_PATH

# remove previous env
conda env remove -n pypeec

# create new env
conda create -y -n pypeec python=3.10

# activate env
conda activate pypeec

# install the base packages
pip install -r requirements.txt

# MKL optional library
conda install -y "mkl-devel=2023.0.0"

# package for creating the package and debugging
pip install "build>=0.10"
pip install "memory-profiler>=0.61"
pip install "gprof2dot>=2022.7"

# Jupyter notebook and PyVista support
pip install "jupyterlab>=3.6"
pip install "pyvista[all,trame]>=0.38"

# FFTW optional library
pip install "pyFFTW>=0.13"

# UMFPACK optional library
pip install "scikit-umfpack>=0.3"

# CuPy optional library
pip install "cupy-cuda11x>=11.6"

# PARDISO optional library
pip install "pydiso>=0.0"

exit 0
