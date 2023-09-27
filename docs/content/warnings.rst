Known Issues
============

PyPEEC Issues
-------------

.. Warning::
    The geometry is meshed with a **regular voxel structure** (uniform grid).
    This implies that large geometries with small features cannot be meshed efficiently.

.. Warning::
    For problems with **magnetic domains**, the **preconditioner** is not optimal.
    This might lead to a slow convergence of the iterative matrix solver.

.. Warning::
    For **large problems**, the code might allocate huge amounts of **memory**.
    This might crash the program and/or your operating system.

.. Warning::
    During the **voxelization** process, the same voxel can be assigned to several domains.
    The problem is solved with used-provided **conflict** resolution rules between the domains.

Library Issues
--------------

.. Warning::
    The **plotting code** is probably sensitive to the environment (platform and the version of the libraries).
    Therefore, these dependencies are minimized and insulated from the rest of the code.
    The plotting code (viewer and plotter) is separated from the simulation code (mesher and solver).

.. Warning::
    **Jupyter** is not included in the package dependencies.
    Inside Jupyter notebooks, IPyWidgets and Trame are used for the rendering.
    Jupyter support is optional, PyPEEC is fully functional without Jupyter.

.. Warning::
    The **GPU libraries** (CuPy and CUDA) are not included in the package dependencies.
    The GPU support is extremely hardware/platform/version dependent.
    GPU support is optional, PyPEEC is fully functional without GPU support.

.. Warning::
    **FFTW, UMFPACK, and MKL/PARDISO** are not included in the package dependencies.
    These libraries can be tricky to install, especially on MS Windows.
    Make sure that these libraries are compiled with multithreading support.
    FFTW, UMFPACK, and MKL/PARDISO are optional, PyPEEC is fully functional without them.

General Issues
--------------

.. Warning::
    Python **Pickle files** are used to store the mesher and solver results.
    Pickling data is not secure. Only load Pickle files that you trust.
    Do not commit the Pickle files in the Git repository.

.. Warning::
    The **dependencies** are under **various licences**.
    Make sure to respect these licenses if you package and/or distribute these libraries.
    Qt is under a copyleft license (LGPL and GPL). FFTW is also under a copyleft license (GPL).
    MKL/PARDISO and CUDA are proprietary software (these libraries are optional).
