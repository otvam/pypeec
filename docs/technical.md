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

PyPEEC is tested on Linux x86/x64 but should run on other platforms.
The following configurations have been tested:
* RedHat 7.9 on x86/x64
* Ubuntu 20.04 on x86/x64
* Ubuntu 22.04 on x86/x64
* NVIDIA T4 Tensor GPU

# Optimization

The code is reasonably optimized, leveraging NumPy and SciPy for the heavy operations.
All the code is vectorized, no loops are used for the array operations.
Sparse matrix algebra is used wherever appropriate to speed up the code and limit the memory consumption.
However, this code is pure Python and advanced optimizations (MKL, MPI, etc.) are not implemented.
Moreover, the memory consumption is not heavily optimized (no customized garbage collection).

The following optional optimizations are available:
* FFTW can be used for computing FFTs (default is SciPy)
* UMFPACK can be used for factorizing sparse matrices (default is SuperLU)
* CuPy can be used for computing FFTs and matrix multiplications with GPUs (default is CPU)

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

## Tests

* The tests are located in the `tests` folder (using the `unittest` framework).
* The shell script `run_tests.sh` is used to run the tests.
* The tests are checking that the examples are running correctly.
* Only integration tests currently exist (no unit tests).

# PyPEEC Warnings

> **Warning**: For problems with magnetic domains, the preconditioner is not heavily optimized.
> This might lead to a very slow convergence of the matrix solver.

> **Warning**: The voxelization of STL files does consider tolerances.
> This implies same the same voxel can be assigned to several domains.
> The problem is solved with used-provided conflict resolution rules.

# Library Warnings

> **Warning**: The plotting code is likely sensitive to the environment (platform and the version of the libraries).
> More particularly, the interactions between **Qt/PyVista/Matplotlib** and **Jupyter/PyVista/Matplotlib**.
> Therefore, the Qt/Jupyter dependencies are minimized and insulated from the rest of the code.

> **Warning**: The optional **GPU libraries** (CUDA, CuPy) should be installed separately.
> These libraries are not included in the package dependencies and environments. 
> The GPU support is extremely platform/version dependent (GPU type and CUDA version).

> **Warning**: **Jupyter Notebook** is not included in the package dependencies and environments.

> **Warning**: The optional **UMFPACK** library is known to be difficult to install on MS Windows.

> **Warning**: The optional **FFTW** library should be compiled with multithreading support.

# General Warnings

> **Warning**: For large problems, the code might allocate huge amounts of memory.
> This might crash the program and/or your operating system.

> **Warning**: Python Pickle files are using to store the mesher and solver results.
> Pickling data is not secure. 
> Only load Pickle files that you trust.
> Do not commit the Pickle files in the Git repository.

> **Warning**: Some dependencies are under copyleft licences.
> Make sure to respect these licenses if you package these libraries.
