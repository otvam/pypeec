# PyPEEC - Installation

## Dependencies Description

* `requirements.txt` - list of Python dependencies (pinned versions)
* `pyproject.toml` - package definition with dependencies (minimum versions)
* `conda_base.yaml` - Conda file with the minimum requirements for PyPEEC
* `conda_dev.yaml` - Conda file including the optional and development packages

## Using a Python Environment

```bash
# Install a Python interpreter
#   - Website: https://www.python.org
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
#   - Website: https://github.com/conda-forge/miniforge
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
