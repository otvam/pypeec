# PyPEEC - 3D FFT-PEEC Solver

## Summary

**PyPEEC** is a **magnetic field solver** with the following characteristics:
* 3D voxel geometry
* FFT-PEEC method
* Extremely fast
* Conductive domain (no magnetic or dielectric media)
* Frequency domain solution
* Connection of current and voltage sources

The **PyPEEC** contains the following tools:
* **ppmesher**: create a 3D voxel structure from STL or PNG files
* **ppviewer**: visualization of the 3D voxel structure
* **ppsolver**: solver for the magnetic field problem
* **ppplotter**: visualization of the problem solution

Different examples are located in the `examples` folder:
* **stl_inductor**: an inductor created from STL files
* **png_inductor**: an inductor created from PNG files
* **voxel_slab**: a simple slab conductor
* **voxel_transformer**: a simple transformer

Different tests are located in the `tests` folder.

## Compatibility

PyPEEC is using the following packages:
* Python
* Numpy and Scipy
* scikit-umfpack (for the solver, optional)
* pyFFTW (for the solver, optional)
* pyvista and imageio (for the mesher)
* pyvista, pyvistaqt, QtPy, PyQt5 (for the viewer and plotter)

PyPEEC is tested on Linux x64 but should run on other platforms.

## Author

* **Thomas Guillod**, Dartmouth College
* [guillod@otvam.ch](mailto:guillod@otvam.ch)
* [https://otvam.ch](https://otvam.ch)

## Copyright

* (c) 2023 - Thomas Guillod - Dartmouth College
