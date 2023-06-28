# PyPEEC - Technical Details

## Dependencies

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

The following **platforms** and systems have been **tested**:
* Linux / RedHat 7.9 on x86/x64
* Linux / Ubuntu 20.04 on x86/x64
* Linux / Ubuntu 22.04 on x86/x64
* MS Windows / Pro 10 21H2 on x86/x64
* GPU / NVIDIA T4 Tensor
* GPU / NVIDIA Tesla K80

The following **platforms** are passing the **automated tests**:
* Linux / Ubuntu 22.04 on x86/x64
* Microsoft / Windows Server 2022 on x86/x64
* Apple / macOS Monterey 12 on x86/x64

If you deploy PyPEEC on computing nodes, GUI libraries (Matplotlib, PyVistaQt, PyQt5) are not required.
If you want to use PyPEEC with Jupyter, PyVista has to be installed with the optional Trame support.

## FFT-Accelerated PEEC Method

There are two main categories of field simulation methods:
* Differential equation based method (FEM, FVM, FD, etc.)
* Integral equation based method (MoM, BEM, PEEC, etc.)

The PEEC method is an integral equation method. The fundamental ideal is to represent
the field simulation problem with a very large distributed equivalent circuit consisting
of resistances, self-inductances, mutual inductances, and capacitances.

This PEEC method feature several advantanges:
* Only the active materials are meshed (no need to mesh the free-space).
* Intuitive understanding of the equation discretization process.
* Straightforward connection of external circuit elements.

The fundamental drawback of the PEEC method is that the matrix describing the
equation system is not sparse. This means that the computational cost and the
memory requirements of the problem is becoming problematic for large systems. 

This problem can be mitigated if the geometry is represented with a voxel structure. 
In this case, the dense matrices are block-Toeplitz Toeplitz-block matrices. 
Such matrices can be embedded into circulant tensors reducing the memory requirements
from O(n^2) to 0(n). Additionally, the matrix-vector multiplications can be done
with Fourier transforms. With an FFT algorithm, the computational complexity of
matrix-vector multiplications is reduced from O(n^2) to 0(n*log(n)). Besides the reduced
computational cost and memory requirement, the FFTs allows for the usage of heavily 
optimized libraries leveraging the parallel processing capabilities of CPUs or GPUs.

Here are some interesting papers about the PEEC method:
* A. Ruehli IEEE TMTT, 10.1109/TMTT.1974.1128204, 1974
* R. Torchio, IEEE TAP, 10.1109/TAP.2019.2927789, 2019
* R. Torchio, IEEE TPEL, 10.1109/TPEL.2021.3092431, 2022

## Optimization

The code is reasonably optimized, leveraging NumPy and SciPy for the heavy operations.
All the code is vectorized, no loops are used for the array operations.
Sparse matrix algebra is used wherever appropriate to speed up the code and limit the memory consumption.
Wherever possible, multithreading/multiprocessing is used for exploiting multicore CPUs.

The following optimizations are available for the computationally heavy operations:
* Computation of the Green functions and electric-magnetic coupling functions.
  * If the distance between the considered voxels is small, an analytical solution is used.
  * If the distance between the considered voxels is large, a numerical approximation is used.
* The factorization of the sparse matrix used for the preconditioner can be done with several algorithms.
  * SuperLU is typically slower but is always available (integrated with SciPy).
  * UMFPACK is typically faster than SuperLU (available through SciKits).
  * MKL/PARDISO is typically faster than UMFPACK (available through Pydiso).
* Two different iterative solvers are available for solving the equation system ("GMRES" or "GCROT").
* The FFTs for computing matrix-vector product with circulant tensors can be done with several algorithms.
  * SciPy FFT library is always available (integrated with SciPy)
  * FFTW has to be installed separately (available through pyFFTW)
  * CuPy is extremely fast but require GPUs with the corresponding libraries (CUDA platform)

## Configuration

* The default configuration file is `pypeec/config.yaml`.
* Afterward, several custom files (if existing) are loaded in the following order:
  * `HOME_DIRECTORY/.pypeec.json` and `HOME_DIRECTORY/.pypeec.yaml`
  * `HOME_DIRECTORY/pypeec.json` and `HOME_DIRECTORY/pypeec.yaml`
  * `CURRENT_DIRECTORY/.pypeec.json` and `CURRENT_DIRECTORY/.pypeec.yaml`
  * `CURRENT_DIRECTORY/pypeec.json` and `CURRENT_DIRECTORY/pypeec.yaml`
* Finally, if set, the filename located the environment variable `PYPEEC` is loaded.

## Packaging and Environment

* A Python package can be built from the `pyproject.toml` and `setup.cfg` files.
* In order to create a minimal Python Virtual Environment, use `requirements.txt`.
* In order to create a minimal Conda Environment, use `conda_base.yaml`.
* In order to create a development environment, use `conda_dev.yaml`.

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

> During the **voxelization** process, the same voxel can be assigned to several domains.
> The problem is solved with used-provided **conflict** resolution rules between the domains.

## Library Warnings

> The **plotting code** is likely sensitive to the environment (platform and the version of the libraries).
> Therefore, these dependencies are minimized and insulated from the rest of the code.
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

> The **dependencies** are under **various licences** (including copyleft and proprietary).
> Make sure to respect these licenses if you package and/or distribute these libraries.
> Qt is under a copyleft license (LGPL and GPL).
> FFTW is under a copyleft license (GPL).
> MKL/PARDISO is a proprietary library (ISSL).
