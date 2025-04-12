Installation
============

Available Packages
------------------

* **Python Package** - available through PyPI
* **Conda Package** - available through conda-forge
* **Dockerfile** - Ubuntu image with PyPEEC and Jupyter

The following **optional libraries are not included** in the PyPI/Conda package:

* **HPC libraries** - FFTW, PyAMG, MKL/FFT, and MKL/PARDISO
* **Notebook support** - JupyterLab, IPyWidgets, Trame, and ipympl
* **GPU libraries** - CuPy and CUDA

Some **important remarks** about the **PyPI/Conda packages**:

* PyPEEC packages are architecture and system independent.
* Some dependencies are architecture and system dependent.
* The optional HPC/GPU libraries are usually easier to install through Conda.
* The Jupyter libraries are usually easier to install through Conda.

Using a Python Environment
--------------------------

.. code-block:: bash

    # Install a Python interpreter
    #   - Website: https://www.python.org/downloads
    #   - Supported versions: 3.10, 3.11, 3.12, and 3.13
    #   - Python executable: "python" or "python3"

    # Create a Python Virtual Environment
    python -m venv venv

    # Activate the Python Virtual Environment
    source venv/bin/activate

    # Install PyPEEC from PyPI
    python -m pip install pypeec

    # Check that PyPEEC is available
    pypeec --version

Using a Conda Environment
-------------------------

.. code-block:: bash

    # Install a Conda distribution
    #   - Website: https://conda-forge.org/download
    #   - Miniforge is sufficient for installing PyPEEC
    #   - Using mamba as a dependency solver is faster

    # Create a Conda Environment with a Python interpreter
    mamba create -n pypeec python=3.11 pypeec

    # Activate the Conda Environment
    mamba activate pypeec

    # Check that PyPEEC is available
    pypeec --version

Using the Docker Image
----------------------

.. code-block:: bash

    # A Dockerfile is also available for building an image
    #   - Contains an Ubuntu image with PyPEEC and Jupyter
    #   - The PyPEEC tutorial and examples are included
    #   - The image is only intended for test purposes

    # Clone the repository
    git clone git@github.com:otvam/pypeec.git && cd pypeec

    # Build the Docker image
    docker build --tag "pypeec:latest" .

    # Run the Docker image
    docker run -p 8888:8888 \
        "pypeec:latest" "start-notebook.py" \
        --NotebookApp.password="" --NotebookApp.token=""

    # Access Jupyter inside the Docker image
    xdg-open "http://127.0.0.1:8888/lab/tree/notebook.ipynb"
