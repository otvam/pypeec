---
title: '
        PyPEEC: A 3D Quasi-Magnetostatic
        Solver using an FFT-Accelerated
        PEEC Method with Voxelization
       '
tags:
  - fft acceleration
  - quasi magnetostatic
  - power electronics
  - peec
  - voxel
  - maxwell
  - python
  - magnetics
authors:
  - name: Thomas Guillod
    orcid: 0000-0003-0738-5823
    corresponding: true
    affiliation: 1
  - name: Charles R. Sullivan
    orcid: 0000-0001-7492-9005
    corresponding: false
    affiliation: 1
affiliations:
  - name: Dartmouth College, NH, USA
    index: 1
date: 20 December 2023
bibliography: paper.bib
---

# Summary

The partial element equivalent circuit method (PEEC) is a particularly 
interesting integral-equation method for electromagnetic problems as it can be 
easily combined with circuit simulations and does not require a discretization 
of the free space. This paper introduces PyPEEC, an open-source Python solver 
targeting 3D quasi-magnetostatic problems such as inductors, transformers, 
chokes, IPT coils, or busbars. The geometry is described with voxels and the 
solver uses an FFT-accelerated variant of the PEEC method. The FFT acceleration 
drastically reduces the computational costs and the memory footprint.

# Statement of Need

Quasi-magnetostatic field simulations are widely used for the design and 
optimization of electrical components (e.g., power electronics, packaging, IC 
design). Among the existing numerical methods (e.g., FEM, FDTD, PEEC, BEM), the 
PEEC method features several advantages [@method_review; @ruehli; @volume_peec]:

- Only the active materials are discretized (no need to mesh the free space).
- Intuitive understanding of the equation discretization process.
- Straightforward connection of external circuit elements.

The fundamental drawback of the classical PEEC method is that the matrix 
describing the equation system is not sparse. This means that the computational 
cost and the memory requirement become problematic for large problems.

This problem can be mitigated if the geometry is represented with voxels 
[@fft_peec; @yucel]. The first advantage of such geometries is that the Green's 
functions (i.e. the inductance and potential matrices) have analytical 
solutions, avoiding computationally intensive numerical integrals [@hoer_exact; 
@piatek_exact]. The second advantage is that, due to the regular voxel 
discretization, many coefficients of the inductance and potential matrices are 
repeated. The dense matrices are block-Toeplitz Toeplitz-block matrices and 
feature the following key properties [@fft_multi_solver; @fft_multi_theory]:

- The block-Toeplitz Toeplitz-block matrices can be embedded into circulant 
tensors reducing the memory requirements from $O(n^2)$ to $O(n)$.
- The matrix-vector multiplications can be done with Fourier transforms. With 
an FFT algorithm, the computational complexity of matrix-vector multiplications 
is reduced from $O(n^2)$ to $O(n \log(n))$. 

Different variants of the FFT-accelerated PEEC method have been shown to be 
extremely fast for a large variety of electromagnetic problems such as 
high-frequency transformers [@fft_peec], power inductors [@marconato], human 
body field exposure [@human_peec], nuclear fusion devices [@bettini], and PCB 
layouts [@grossner].

An open-source implementation ("FFT-PEEC") of the FFT-accelerated PEEC method 
already exists [@peec_code; @nlie_code]. However, this code can only handle 
magnetic materials for static simulations (and not in the frequency domain). 
Moreover, depending on the considered quasi-static problem (e.g. geometries 
with multiple conductors), the source code requires some adaptations. The 
open-source tools "VoxHenry" and "MARIE" are also used FFT-accelerated methods 
but are specialized for full-wave solutions without magnetic materials 
[@vox_code; @marie_code]. Finally, it should be noted that all the 
aforementioned implementations depend on proprietary programming languages and 
libraries.

PyPEEC, the tool introduced in this paper, addresses these needs by providing a 
3D quasi-magnetostatic implementation of the FFT-accelerated PEEC method 
[@fft_peec]. PyPEEC is a fully open-source (MPL\ 2.0 licence and implemented in 
Python) and offers a general-purpose solver by allowing the description of 
arbitrary problems without having to modify the source code.

# Capabilities and Workflow

In this paper, the release 4.16 of PyPEEC is considered. PyPEEC solves 3D 
magnetostatic and quasi-magnetostatic problems with voxel geometries. An 
arbitrary number of conductive domains, magnetic domains (ideal and/or lossy), 
and sources (voltage and/or current) can be used. The current density, flux 
density, potential, loss density, and energy density are computed. The 
free-space magnetic field (near-field) can also be computed on a point cloud. 
Additionally, the voltage, current, complex power, and impedance of the 
different terminals are extracted.

PyPEEC is implemented in pure Python using NumPy, SciPy, Joblib, Rasterio, 
Shapely, Pillow, Matplotlib, and PyVista. The solver is able to leverage 
multi-core CPUs and GPUs. Optional HPC libraries are available for accelerating 
the sparse preconditioner factorization (MKL/PARDISO, UMFPACK, and PyAMG) and 
the FFT operations (FFTW and CuPy/CUDA). PyPEEC can be used through an API, a 
command-line tool, or Jupyter notebooks.

![PyPEEC workflow consisting of the *mesher*, *solver*, *viewer*, and 
*plotter*](workflow.pdf){#fig:workflow width="100%"}

\autoref{fig:workflow} depicts the PyPEEC workflow. First the *mesher* builds 
the geometry (from vector shapes, STL files, PNG files, or GERBER files), 
performs the voxelization, and checks the validity of the discretization. 
Afterward, the *solver* creates the FFT-multiplication operators, assembles the 
equation systems, solves the problem, and post-processes the solution. The 
*viewer* and the *plotter* are used to visualize the results.

# Solver Performance

To demonstrate the performance of the solver, a planar air-core spiral inductor 
is considered. The inductor has a footprint of 4\ mm^2^ and is operated in the 
40.68\ MHz ISM band. \autoref{fig:performance} shows the ratio between the AC 
and DC current densities, the relative error on the extracted impedance, and 
the computational cost. The number of degrees of freedom represents the number 
of unknowns for the PEEC problem. The computational cost is evaluated with an 
AMD\ EPYC\ 7543\ CPU.

![(a)\ Ratio between the AC and DC current densities. (b)\ Relative error on 
the extract equivalent resistance and the inductance. (c)\ Wall clock time 
duration for the complete workflow.](performance.pdf){#fig:performance 
width="100%"}

As the skin depth is smaller than the dimension of the conductor, the eddy 
currents are non-negligible. This implies that, with a coarse discretization, 
the resistance value is less accurate than the inductance value. With a 
tolerance of 4%, the quasi-static problem is solved in 4 seconds. The FFT 
acceleration allows dense PEEC problems with 10^7^ degrees of freedom to be 
solved in 80 seconds.

# Acknowledgments
  
This work was supported by the Power Management Integration Center (NSF IUCRC) 
at Dartmouth College under Grant No. PMIC-062. The authors would like to thank 
Yue (Will) Wu for discovering and reporting several bugs.

# References

