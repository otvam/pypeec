# PyPEEC - Technical Details

## Dependencies

**PyPEEC** is entirely programmed in **Python 3** and is using the following packages:
* PyYAML (used everywhere)
* NumPy (used everywhere)
* SciPy (used everywhere)
* Pillow (for the mesher)
* VTK, PyVista (for the mesher, viewer, and plotter)
* Matplotlib (for the viewer and plotter)
* PyVistaQt, QtPy, PyQt5 (for the viewer and plotter)

The following optional packages are used for speeding up the solver:
* scikit-umfpack (for the solver)
* pyFFTW (for the solver)
* CuPy (for the solver)

The following platform and system configurations have been tested:
* Linux / RedHat 7.9 on x86/x64
* Linux / Ubuntu 20.04 on x86/x64
* Linux / Ubuntu 22.04 on x86/x64
* MS / Windows 10 21H2 on x86/x64
* GPU / NVIDIA T4 Tensor GPU

## Optimization

The code is reasonably optimized, leveraging NumPy and SciPy for the heavy operations.
All the code is vectorized, no loops are used for the array operations.
Sparse matrix algebra is used wherever appropriate to speed up the code and limit the memory consumption.
Wherever possible, multithreading is used for exploiting multicore CPUs.

The following optional optimizations are available:
* FFTW can be used for computing FFTs (default is SciPy)
* CuPy can be used for computing FFTs and matrix multiplications with GPUs (default is NumPy/SciPy))
* UMFPACK pr MKL/PARDISO can be used for factorizing sparse matrices (default is SuperLU)

Advanced optimizations (MKL, MPI, OpenMP, or C/FORTRAN) are not implemented.
Moreover, the memory consumption is not heavily optimized.

## Configuration

The default configuration file is `pypeec/pypeec.yaml`.
The default configuration file is loaded at the startup.
Afterwards, a custom configuration (JSON or YAML) file can be set:
* with a function call (see `pypeec.main` module)
* with a command line option (see `pypeec.script` module)

## Packaging and Environment

* A Python package can be built from the `pyproject.toml` and `setup.cfg` files.
* In order to create a Python Virtual Environment, use `requirements.txt`.
* In order to create a Conda Environment, use `conda.yml`.
* In order to create a development environment, use `run_env.sh`.

## Tests

* The tests are located in the `tests` folder (using the `unittest` framework).
* The shell script `run_tests.sh` is used to run the tests.
* The tests are checking that the examples are running correctly.
* Only integration tests currently exist (no unit tests).

## PyPEEC Warnings

> For problems with **magnetic domains**, the **preconditioner** is not optimal.
> This might lead to a slow convergence of the iterative matrix solver.

> For **large problems**, the code might allocate huge amounts of **memory**.
> This might crash the program and/or your operating system.

> During the **voxelization of STL** files, the same voxel can be assigned to several domains.
> The problem is solved with used-provided **conflict** resolution rules between the domains.

## Library Warnings

> The **plotting code** is likely sensitive to the environment (platform and the version of the libraries).
> Therefore, the Qt and Jupyter dependencies are minimized and insulated from the rest of the code.
> The plotting code (viewer and plotter) is separated from the simulation code (mesher and solver).

> **Jupyter** is not included in the package dependencies.
> For Jupyter, PyVista has to be installed with the optional Trame support.
> Jupyter support is optional, PyPEEC is fully functional without Jupyter.

> The **GPU libraries** (CuPy and CUDA) are not included in the package dependencies.
> The GPU support is extremely hardware/platform/version dependent.
> GPU support is optional, PyPEEC is fully functional without GPU support.

> **FFTW, UMFPACK, and MKL/PARDISO** are not included in the package dependencies.
> These libraries can be tricky to install, especially on MS Windows.
> Make sure that these libraries are compiled with multithreading support.
> FFTW, UMFPACK, and MKL/PARDISO are optional, PyPEEC is fully functional without them.

## General Warnings

> Python **Pickle files** are using to store the mesher and solver results.
> Pickling data is not secure. 
> Only load Pickle files that you trust.
> Do not commit the Pickle files in the Git repository.

> Some **dependencies** are under **various licences** (including copyleft and proprietary).
> Make sure to respect these licenses if you package and/or distribute these libraries.
> Qt is under different copyleft licenses (GPL and LGPL).
> FFTW is under a copyleft license (GPL).
> MKL/PARDISO is a proprietary library (ISSL).
