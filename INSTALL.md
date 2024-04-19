# PyPEEC - Installation

## Using a Python Environment

```bash
# Install a Python interpreter
#   - Python website: https://www.python.org
#   - Supported versions: 3.9, 3.10, 3.11, and 3.12

# Create a Python Virtual Environment
python -m venv venv

# Activate the Python Virtual Environment
source venv/bin/activate

# Install PyPEEC from PyPi
python -m pip install pypeec

# Check that PyPEEC is available
pypeec --version
```

## Using a Conda Environment

```bash
# Install a Python interpreter
#   - Conda website: https://conda.io
#   - Miniconda is sufficient for PyPEEC

# Create a Conda Environment with the packages
#   - conda_base.yaml: minimum requirements for PyPEEC
#   - conda_dev.yaml: optional and development packages 
conda env create -f conda_base.yaml
# OR
conda env create -f conda_dev.yaml

# Activate the Conda Environment
conda activate pypeec

# Install PyPEEC from PyPi
pip install --no-deps pypeec

# Check that PyPEEC is available
pypeec --version
```
