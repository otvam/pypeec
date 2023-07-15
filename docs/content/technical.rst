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

* UMFPACK (available through SciKits)
* MKL/PARDISO (available through Pydiso)
* FFTW (available through pyFFTW)
* CuPy (using GPUs through CUDA)

Platforms
---------

The main **target platform** of PyPEEC is **Linux**.
The following **platforms** and systems have been **tested**:

* Linux / RedHat 7.9 on x86/x64
* Linux / Ubuntu 20.04 on x86/x64
* Linux / Ubuntu 22.04 on x86/x64
* Apple / macOS Ventura 13 on M1 Pro
* MS Windows / Pro 10 21H2 on x86/x64

The following **GPUs** have been tested:

# GPU / NVIDIA RTX 2070 Max-Q
* GPU / NVIDIA T4 Tensor
* GPU / NVIDIA Tesla K80

The following **platforms** are passing the **automated tests**:

* Linux / Ubuntu 22.04 on x86/x64
* Microsoft / Windows Server 2022 on x86/x64
* Apple / macOS Monterey 12 on x86/x64

If you deploy PyPEEC on computing nodes, GUI libraries (Matplotlib, PyVistaQt, PyQt5) are not required.
If you want to use PyPEEC with Jupyter, PyVista has to be installed with the optional Trame support.

Configuration File
------------------

* The default configuration file is ``pypeec/config.yaml``.

    * This file is always loaded first.
    * This file is included in the package.

* The filename located the environment variable ``PYPEEC`` is loaded.

    * If the variable is not set, the default configuration is kept.
    * If the variable is is set, the default configuration is replaced.
    * This file can be in JSON or YAML formats.

Packaging and Environment
-------------------------

* A Python package can be built from the ``pyproject.toml`` and ``setup.cfg`` files.
* In order to create a minimal Python Virtual Environment, use ``requirements.txt``.
* In order to create a minimal Conda Environment, use ``conda_base.yaml``.
* In order to create a development environment, use ``conda_dev.yaml``.

Automated Tests
---------------

* The tests are located in the ``tests`` folder (using the ``unittest`` framework).
* The shell script ``run_tests.sh`` is used to run the tests.
* The tests are checking that the examples are running correctly.
* Only integration tests currently exist (no unit tests).

Sphinx Documentation
--------------------

* The documentation is located in the ``docs`` folder (using the ``Sphinx`` generator).
* The shell script ``run_docs.sh`` is used to build the HTML documentation.