Technical Details
=================

Dependencies
------------

**PyPEEC** is entirely programmed in **Python 3** and has the following dependencies:

* PyYAML (configuration file format)
* NumPy, SciPy, and Joblib (numerical libraries)
* Pillow (for the mesher, image manipulation)
* Shapely and Rasterio (for the mesher, 2D shape manipulation)
* VTK and PyVista (for the mesher, 3D shape manipulation)

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
* Linux / Debian 12.4 on x86/x64
* Linux / Ubuntu 20.04 on x86/x64
* Linux / Ubuntu 22.04 on x86/x64

The following **platforms** and systems have been  **partially tested**:

* Apple / macOS Monterey 12 on x86/x64
* Apple / macOS Ventura 13 on M1 Pro
* MS Windows / Pro 10 on x86/x64
* MS Windows / Pro 11 on x86/x64

The following **GPUs** have been tested (CUDA / CuPy compatible):

* GPU / NVIDIA RTX 2070
* GPU / NVIDIA T4 Tensor
* GPU / NVIDIA Tesla K80
* GPU / NVIDIA RTX 3090

The following **platforms** are passing the **automated tests**:

* Linux / Ubuntu 22.04 on x86/x64
* Microsoft / Windows Server 2022 on x86/x64
* Apple / macOS Monterey 12 on x86/x64

The following **Python version** are passing the **automated tests**:

* CPython 3.9
* CPython 3.10
* CPython 3.11
* CPython 3.12

Logger Configuration File
-------------------------

* The default logger configuration file is located in ``pypeec/data/logger.yaml``.
* A custom logger configuration file can set with an environment variable.
* If the ``PYTHONLOGGER`` variable is not set, the default configuration is kept.
* If the ``PYTHONLOGGER`` variable is is set, the default configuration is replaced.
* The ``PYTHONLOGGER`` variable should contain a path towards the YAML configuration.

Packaging and Environment
-------------------------

* List of Python dependencies (pinned versions): ``requirements.txt``
* Package definition with dependencies (minimum versions): ``pyproject.toml``
* Conda file with the minimum requirements for PyPEEC: ``conda_base.yaml``
* Conda file including the optional and development packages: ``conda_dev.yaml``
* Conda feedstock recipe: https://github.com/conda-forge/pypeec-feedstock

Tests and Documentation
-----------------------

* The documentation is located in the ``docs`` folder (using the ``sphinx`` generator).
* The tests are located in the ``tests`` folder (using the ``unittest`` framework).
* The tests are checking that the examples are running correctly.
* Only integration tests currently exist (no unit tests).

Scripts
-------

* ``scripts/run_tests.sh``: run all the tests.
* ``scripts/run_coverage.sh``: run a code coverage analysis.
* ``scripts/run_build.sh``: build the Python package and build the HTML documentation.
* ``scripts/run_release.sh``: create a release (tag, release, package, and documentation).

Contributing
------------

PyPEEC is welcoming contributions (code, documentation, example, benchmark, test, tutorial, etc.) !
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
