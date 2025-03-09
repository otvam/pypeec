Known Issues
============

PyPEEC Issues
-------------

.. note::
    The geometry is meshed with a **regular voxel structure** (uniform grid).
    This implies that large geometries with small features cannot be meshed efficiently.

.. note::
    If should be noted than the **inductance** is only fully defined for closed loops.
    For non-closed loops, only the concept of **partial inductance** is well defined.

.. note::
    The **magnetic near-field** computation is done with **lumped variables**.
    Therefore, the computation is only accurate far away from the voxel structure.

.. note::
    For problems with **magnetic domains**, the **preconditioner** is not optimal.
    This might lead to a slow convergence of the iterative matrix solver.
    For such cases, using the segregated solver approach might be useful.

.. note::
    It should be noted that **surface charges** are not considered.
    Only volume charges are used, which is an approximation.

.. note::
    During the **voxelization** process, the same voxel can be assigned to several domains.
    The problem is solved with used-provided **conflict** resolution rules between the domains.

Library Issues
--------------

.. important::
    The **plotting code** is probably sensitive to the environment (platform and version of the libraries).
    Particularly, using the Wayland display system (instead of X11) is creating several issues.
    The plotting code (viewer and plotter) is separated from the simulation code (mesher and solver).
    Hence, these graphical dependencies are minimized and insulated from the rest of the code.

.. important::
    **Jupyter** is not included in the default package dependencies.
    Inside Jupyter notebooks, IPyWidgets Trame, and ipympl are used for the rendering.
    Jupyter support is optional, PyPEEC is fully functional without Jupyter.

.. important::
    The **GPU libraries** (CuPy and CUDA) are not included in the package dependencies.
    The GPU support is extremely hardware/platform/version dependent.
    GPU support is optional, PyPEEC is fully functional without GPU support.

.. important::
    **FFTW, PyAMG, MKL/FFT, and MKL/PARDISO** are not included in the default package dependencies.
    These libraries can be tricky to install, especially on MS Windows or Apple MacOS.
    The aforementioned libraries are optional, PyPEEC is fully functional without them.

General Issues
--------------

.. warning::
    Python **Pickle files** can be used to store the mesher and solver results.
    Pickling data is not secure. Only load Pickle files that you trust.
    JSON/MessagePack files can be used to solve this problem.

.. warning::
    The **Docker image** is only intended for test purposes.
    This image is not screened for eventual vulnerabilities.
    Do not use the image for public-facing servers.

.. warning::
    The **dependencies** are under **various licences**.
    Make sure to respect these licenses if you package and/or distribute these libraries.
    Qt is under a copyleft license (LGPL and GPL). FFTW is also under a copyleft license (GPL).
    INTEL/MKL and NVIDIA/CUDA are proprietary software (these libraries are optional).
