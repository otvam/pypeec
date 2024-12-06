Technical Details
=================

Dependencies
------------

**PyPEEC** is entirely programmed in **Python 3** and has the following dependencies:

* SciLogger, SciSave, and jsonschema (logging and serialization)
* NumPy, SciPy, and Joblib (basic numerical computing libraries)
* Shapely and Rasterio (only used for the mesher, 2D shape manipulation)
* Pillow (only used for the mesher, 2D image manipulation)
* VTK and PyVista (only used for for the mesher, 3D shape manipulation)

Additionally, the following **libraries** are used for the **plotter** and **viewer**:

* Matplotlib and PyQt5 (2D plots)
* VTK, PyVista, PyVistaQt, and PyQt5 (3D plots)

The following **optional packages** can be used for **speeding up** the solver:

* PyAMG (Python Algebraic Multigrid)
* MKL/FFT (available through mkl_fft)
* MKL/PARDISO (available through Pydiso)
* FFTW (available through pyFFTW)
* CuPy (using GPUs through CUDA)

The following **optional packages** are required for **Jupyter notebooks**:

* JupyterLab
* IPyWidgets
* Trame

Supported Platforms
-------------------

The main **target platform** of PyPEEC is **Linux** on x86/x64/glibc:

* Linux / RedHat 7.9 on x86/x64/glibc
* Linux / RedHat 8.7 on x86/x64/glibc
* Linux / Debian 12.4 on x86/x64/glibc
* Linux / Ubuntu 20.04 on x86/x64/glibc
* Linux / Ubuntu 22.04 on x86/x64/glibc
* Linux / Ubuntu 24.04 on x86/x64/glibc

The following **platforms** and systems have been  **partially tested**:

* Apple macOS Monterey 12 on x86/x64
* Apple macOS Ventura 13 on ARM64
* Apple macOS Sonoma 14 on ARM64
* MS Windows / Pro 10 on x86/x64
* MS Windows / Pro 11 on x86/x64

The following **GPUs** have been tested (CUDA / CuPy compatible):

* NVIDIA RTX 2070
* NVIDIA RTX 3090
* NVIDIA T4 Tensor
* NVIDIA Tesla K80

The following **platforms** are passing the **automated tests**:

* Linux / Ubuntu 22.04 on x86/x64
* Microsoft / Windows Server 2022 on x86/x64
* Apple / macOS Sonoma 14 on ARM64

The following **Python version** are passing the **automated tests**:

* CPython 3.10
* CPython 3.11
* CPython 3.12

Logger and Data Serialization
-----------------------------

For the logger, PyPEEC is using **SciLogger**:

* Custom logger configuration files can be set with the  ``SCILOGGER`` environment variable.
* More information on the logging module: https://github.com/otvam/scilogger

For the serialization, PyPEEC is using **SciSave**:

* The input/configuration files are either JSON or YAML files.
* The output/data files are either JSON or Pickle files.
* Pickle is faster than JSON for large output/data files.
* More information on the serialization module: https://github.com/otvam/scisave

Packaging and Environment
-------------------------

The following files are describing the packages and dependencies:

* Definition of the Python package: ``pyproject.toml``
* Dockerfile and dependencies for building the Docker image: ``docker``
* Conda feedstock recipe: https://github.com/conda-forge/pypeec-feedstock

The development environment is defined in ``conda.yaml``:

* Contains all the required and optional dependencies.
* Contains the packaging/development tools.
* All the version number are pinned.
* Tested with Linux x86/x64/glibc.

The following scripts are used to build the package, documentation, and releases:

* ``scripts/run_build.sh``: build the Python package and build the HTML documentation.
* ``scripts/run_release.sh``: create a release (tag, release, package, and documentation).

Tests and Coverage
------------------

PyPEEC is using different tests to check for potential regressions:

* The tests are located in the ``tests`` folder.
* The tests are using the ``unittest`` framework.
* The tests are covering all the main functionalities.
* The tests are using the examples and the tutorial to check the code.
* Only integration tests are currently implemented (no unit tests).

These files are used to run the tests (locally and/or continuous integration):

* ``scripts/run_tests.sh``: run all the integration tests.
* ``scripts/run_coverage.sh``: run a code coverage analysis.

Contributing
------------

PyPEEC is gladly accepting contributions (code, benchmark, packages, or tests).
Non-code contributions (documentation, examples, or tutorials) are particularly welcomed.
For large contributions, please first discuss the changes in the issue tracker.

Bug Report
----------

* The **version of PyPEEC and Python**.
* The **operating system/platform/hardware**.
* A **clear and concise description** of the bug.
* A **minimal working example** for the bug.
* For PyVista related bugs, please include the ``pyvista.Report`` output.
* For NumPy related bugs, please include the ``numpy.show_config`` output.
* For SciPy related bugs, please include the ``scipy.show_config`` output.
