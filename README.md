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
* **mesher**: create a 3D voxel structure from STL or PNG files
* **viewer**: visualization of the 3D voxel structure
* **solver**: solver for the magnetic field problem
* **plotter**: visualization of the problem solution

All the modules and packages are located in the `PyPEEC` folder.
The module `PyPEEC.script` contains the entry point scripts.
Different command line scripts are defined: `ppmesher`, `ppviewer`, `ppsolver`, and `ppplotter`.

Different examples are located in the `examples` folder:
* **stl_inductor**: an inductor created from STL files
* **png_inductor**: an inductor created from PNG files
* **voxel_slab**: a simple slab conductor
* **voxel_transformer**: a simple transformer

The tests are located in the `tests` folder and can be run with `python -m unittest -v`.

## Gallery

![viewer](docs/viewer.png)

![plotter_potential](docs/plotter_potential.png)

![plotter_current](docs/plotter_current.png)


## Compatibility

PyPEEC is using the following packages:
* Python 3
* Numpy and Scipy
* scikit-umfpack (for the solver, optional)
* pyFFTW (for the solver, optional)
* pyvista and imageio (for the mesher)
* pyvista, pyvistaqt, QtPy, PyQt5 (for the viewer and plotter)

PyPEEC is tested on Linux x64 but should run on other platforms.

The package can be built with `python -m build`.

## Author

* **Thomas Guillod**, Dartmouth College
* [guillod@otvam.ch](mailto:guillod@otvam.ch)
* [https://otvam.ch](https://otvam.ch)

## Copyright

* (c) 2023 - Thomas Guillod - Dartmouth College
