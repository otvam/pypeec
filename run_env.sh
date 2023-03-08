#!/bin/bash
# Script for creating the development environment:
#   - using Conda for Python and MKL
#   - using Pip for the Python packages
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

# package for building the package
pip install "build>=0.10"

# Jupyter notebook
pip install "jupyterlab>=3.6"

# Jupyter support for PyVista
pip install "pyvista[all,trame]>=0.38"

# FFTW optional library
pip install "pyFFTW>=0.13"

# UMFPACK optional library
pip install "scikit-umfpack>=0.3"

# MKL optional library
conda install -y "mkl-devel=2023.0.0"

# MKL/PARDISO optional library
pip install "pydiso>=0.0"

# CuPy optional library
pip install "cupy-cuda11x>=11.6"

exit 0
