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

The following **optional packages** can be used for speeding up the solver:

* PyAMG (pure Python solver)
* UMFPACK (available through SciKits)
* MKL/PARDISO (available through Pydiso)
* FFTW (available through pyFFTW)
* CuPy (using GPUs through CUDA)

If you deploy PyPEEC on computing nodes, the GUI libraries (Matplotlib, PyVistaQt, PyQt5) are not required.
Inside Jupyter notebooks, IPyWidgets and Trame are used for the rendering.

Supported Platforms
-------------------

The main **target platform** of PyPEEC is **Linux** on x86/x64:

* Linux / RedHat 7.9 on x86/x64
* Linux / RedHat 8.7 on x86/x64
* Linux / Debian 12.4 on x86/x64
* Linux / Ubuntu 20.04 on x86/x64
* Linux / Ubuntu 22.04 on x86/x64
* Linux / Ubuntu 24.04 on x86/x64

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

* Linux / Ubuntu 22.04 on x86/x64 / Conda / PyPi
* Microsoft / Windows Server 2022 on x86/x64 / Conda / PyPi
* Apple / macOS Sonoma 14 on ARM64 / Conda

The following **Python version** are passing the **automated tests**:

* CPython 3.10
* CPython 3.11
* CPython 3.12

Logger and Data Serialization
-----------------------------

For the logger, PyPEEC is using **SciLogger**:

* Custom logger configuration files can be set with the  ``SCILOGGER`` environment variable.
* More information about the logging module: https://github.com/otvam/scilogger

For the serialization, PyPEEC is using **SciSave**:

* The input/configuration files are either JSON or YAML files.
* The output/data files are either JSON or Pickle files.
* More information about the serialization module: https://github.com/otvam/scisave

Packaging and Environment
-------------------------

The following files are describing the package, documentation, and dependencies:

* List of Python dependencies (pinned versions): ``requirements.txt``
* Package definition with dependencies (minimum versions): ``pyproject.toml``
* Conda file with the minimum requirements for PyPEEC: ``conda_base.yaml``
* Conda file including the optional and development packages: ``conda_dev.yaml``
* Conda feedstock recipe: https://github.com/conda-forge/pypeec-feedstock
* The examples and the tutorial are located in the ``examples`` folder.
* The Sphinx documentation is located in the ``docs`` folder.

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

PyPEEC is welcoming contributions (code, documentation, example, benchmark, test, tutorial, etc.)!
For large changes, please first discuss the change you wish to make in the issue tracker.

Bug report
----------

Please include a clear and concise description of what the bug is.
Ideally, provide a minimal working example for the bug.

Additionally, please report the following parameters:

* The version of the PyPEEC you are using.
* The platform/hardware you are using.
* The version of Python and of the relevant dependencies.
* For PyVista related bugs, please include the ``pyvista.Report`` output.
* For NumPy related bugs, please include the ``numpy.show_config`` output.
* For SciPy related bugs, please include the ``scipy.show_config`` output.
