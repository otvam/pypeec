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

Configuration File
------------------

* The default configuration file is ``pypeec/data/config.yaml``.

    * This file is always loaded first.
    * This file is included in the package.

* The default configuration file can be extracted with the ``pypeec config`` command.

* The filename located the environment variable ``PYPEEC`` is loaded.

    * If the variable is not set, the default configuration is kept.
    * If the variable is is set, the default configuration is replaced.
    * This file can be in JSON or YAML formats.

Packaging and Environment
-------------------------

* A Python package can be built from the ``pyproject.toml`` file.
* In order to create a minimal Python Virtual Environment, use ``requirements.txt``.
* In order to create a minimal Conda Environment, use ``conda_base.yaml``.
* In order to create a full development environment, use ``conda_dev.yaml``.

Tests and Documentation
-----------------------

* The documentation is located in the ``docs`` folder (using the ``sphinx`` generator).
* The tests are located in the ``tests`` folder (using the ``unittest`` framework).
* The tests are checking that the examples are running correctly.
* Only integration tests currently exist (no unit tests).

Scripts
-------

* ``run_tests.sh``: run all the tests.
* ``run_coverage.sh``: run a code coverage analysis.
* ``run_build.sh``: build the Python package and build the HTML documentation.
* ``run_release.sh``: create a release (tag, release, package, and documentation).

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
