Implementation
===============

FFT-Accelerated PEEC Method
---------------------------

There are two main categories of field simulation methods:

* Differential equation based method (FEM, FD, etc.)
* Integral equation based method (MoM, FVM, PEEC, etc.)

The PEEC method is an integral equation method. The fundamental idea is to represent
the field simulation problem with a very large distributed equivalent circuit consisting
of resistances, self-inductances, mutual inductances, and capacitances.

This PEEC method features several advantanges:

* Only the active materials are discretized (no need to mesh the free-space).
* Intuitive understanding of the equation discretization process.
* Straightforward connection of external circuit elements.

The fundamental drawback of the PEEC method is that the matrix describing the
equation system is not sparse. This means that the computational cost and the
memory requirements are becoming problematic for large systems.

This problem can be mitigated if the geometry is represented with a voxel structure. 
In this case, the dense matrices are block-Toeplitz Toeplitz-block matrices. 
Such matrices can be embedded into circulant tensors reducing the memory requirements
from O(n^2) to O(n). Additionally, the matrix-vector multiplications can be done
with Fourier transforms. With an FFT algorithm, the computational complexity of
matrix-vector multiplications is reduced from O(n^2) to O(n*log(n)). Besides the reduced
computational cost and memory requirement, the FFTs allows for the usage of heavily 
optimized libraries leveraging the parallel processing capabilities of CPUs or GPUs.

PyPEEC is using voxels to describe the geometry and, therefore, can take advantage
of the FFT acceleration. This implies that PEEC problems with several millions of
voxels can be solved in a few minutes on a laptop computer.

Here are some interesting papers about the PEEC method:

* A. Ruehli IEEE TMTT, 10.1109/TMTT.1974.1128204, 1974
* R. Torchio, IEEE TAP, 10.1109/TAP.2019.2927789, 2019
* R. Torchio, IEEE TPEL, 10.1109/TPEL.2021.3092431, 2022

Numerical Optimization
----------------------

The code is reasonably optimized, leveraging NumPy and SciPy for the heavy operations.
All the code is vectorized, no loops are used for the array/matrix/tensor operations.
Sparse matrix algebra is used wherever appropriate to speed up the code and limit the memory consumption.
Wherever possible, multithreading/multiprocessing is used for exploiting multicore CPUs.

The following optimizations are available for the computationally heavy operations:

* Computation of the Green functions and electric-magnetic coupling functions.

  * If the distance between the considered voxels is small, an analytical solution is used.
  * If the distance between the considered voxels is large, a numerical approximation is used.

* The factorization of the preconditioner sparse matrix can be done with several algorithms.

  * SuperLU is typically slower but is always available (integrated with SciPy).
  * UMFPACK is typically faster than SuperLU (available through SciKits).
  * MKL/PARDISO is typically faster than UMFPACK (available through Pydiso).
  * PyAMG is typically slow but uses less memory (risk of convergence issues).

* Two different iterative solvers are available for the dense matrices.

  * GMRES - Generalized Minimal RESidual algorithm
  * GCROT - Flexible GCROT(m,k) algorithm

* The FFTs for computing matrix-vector product can be done with several algorithms.

  * SciPy FFT library is always available (integrated with SciPy)
  * FFTW has to be installed separately (available through pyFFTW)
  * CuPy is extremely fast but require GPUs compatible with the CUDA toolkit

* The ``file_tolerance`` input file is setting up all the numerical parameters:

  * Definition of the numerical options and tolerances.
  * Selection of the library used for numerical operations.
  * Definition of the multithreading/multiprocessing options.
  * The complete file format is documented in ``examples/config/tolerance.yaml``.
