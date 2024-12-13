Technical Details
=================

Dependencies
------------

**PyPEEC** is entirely programmed in **Python 3** and has the following **dependencies**:

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
* Trame / ipympl

Supported Platforms
-------------------

PyPEEC is known to **work** with the following **platforms**:

* Linux on x86/x64/glibc
* Apple macOS on x86/x64
* Apple macOS on ARM64
* MS Windows on x86/x64

Some more **details** on the supported **platforms**:

* The main **target platform** of PyPEEC is **Linux** on x86/x64/glibc.
* PyPEEC is a **pure-python package** and should work on any platform.
* Any **CUDA and CuPy** compatible **GPU** is supported.
* Compatible **Python versions**: 3.10, 3.11, and 3.12

Logger and Data Serialization
-----------------------------

For the logging, PyPEEC is using **SciLogger**:

* The logger configuration files can be set with the  ``SCILOGGER`` environment variable.
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
* Dockerfile for building the Docker image: ``Dockerfile``
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

The following **automated tests** are performed:

* Test the latest version of the released Conda and PyPI pakages
* Test the Conda and PyPI environments with the current Git code

The following **platforms** are considered for the **automated tests**:

* Linux / Ubuntu on x86/x64
* Microsoft / Windows on x86/x64
* Apple / macOS on ARM64

The following **Python versions** are considered for the **automated tests**:

* CPython 3.10
* CPython 3.11
* CPython 3.12

Contributing and Bug Report
---------------------------

PyPEEC is gladly accepting contributions (code, benchmark, packages, or tests).
Non-code contributions (documentation, examples, or tutorials) are particularly welcomed.
For large contributions, please first discuss the changes in the issue tracker.

For the bug reports, please report the following information:

* The **version of PyPEEC and Python**.
* The **operating system/platform/hardware**.
* A **clear and concise description** of the bug.
* A **minimal working example** for the bug.
* For PyVista related bugs, please include the ``pyvista.Report`` output.
* For NumPy related bugs, please include the ``numpy.show_config`` output.
* For SciPy related bugs, please include the ``scipy.show_config`` output.
