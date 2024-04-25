# PyPEEC - Installation

## Available Packages

* **Python Package** - available through PyPI
* **Conda Package** - available through conda-forge

PyPEEC packages are generic (architecture and system independent packages).
However, some dependencies are architecture and system dependent packages.
The optional HPC libraries are usually easier to install through Conda.

## Using a Python Environment

```bash
# Install a Python interpreter
#   - Website: https://www.python.org/downloads
#   - Supported versions: 3.9, 3.10, 3.11, and 3.12
#   - Python executable: "python" or "python3"

# Create a Python Virtual Environment
python -m venv pypeecenv

# Activate the Python Virtual Environment
source venv/bin/activate

# Install PyPEEC from PyPi
python -m pip install pypeec

# Check that PyPEEC is available
pypeec --version
```

## Using a Conda Environment

```bash
# Install a Conda distribution
#   - Website: https://conda-forge.org/download
#   - Miniforge is sufficient for installing PyPEEC
#   - Using mamba as a dependency solver is faster

# Create a Conda Environment with a Python interpreter
mamba create -n pypeec_venv python=3.10

# Activate the Conda Environment
mamba activate pypeec_venv

# Install PyPEEC from conda-forge
mamba install conda-forge::pypeec

# Check that PyPEEC is available
pypeec --version
```
