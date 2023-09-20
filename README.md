# PyPEEC - 3D PEEC Solver

> * **Website: [pypeec.otvam.ch](https://pypeec.otvam.ch)**
> * **Repository: [github.com/otvam/pypeec](https://github.com/otvam/pypeec)**
> * **Package: [pypi.org/project/pypeec](https://pypi.org/project/pypeec)**

## Summary

**PyPEEC** is a **3D quasi-magnetostatic PEEC solver** developed at **Dartmouth College** within the Power Management Integration Center (PMIC). 
PyPEEC is a **fast solver** (FFT and GPU accelerated) that can simulate a large variety of **magnetic components** (inductors, transformers, chokes, IPT coils, busbars, etc.). 
The tool contains a **mesher** (STL, PNG, and GERBER formats), a **solver** (static and frequency domain), and **advanced plotting** capabilities.
The code is written in **Python** and is fully **open source**!

## Capabilities

**PyPEEC** features the following **characteristics**:
* **PEEC method** with **FFT acceleration**
* Representation of the **geometry** with **3D voxels**
* **Multithreading** and **GPU acceleration** are available
* **Fast** with **moderate memory** requirements
* Import the **geometry** from **STL**, **PNG**, and **GERBER** files
* Draw the **geometry** with stacked 2D **vector shapes** or **voxel indices**
* **Pure Python** and **open source** implementation
* Can be used from the **command line**
* Can be used with **Jupyter notebooks**
* Advanced **plotting** capabilities

**PyPEEC** solves the following **3D quasi-magnetostatic problems**:
* Frequency domain solution (DC and AC)
* Conductive and magnetic domains (ideal or lossy)
* Connection of current and voltage sources
* Extraction of the loss and energy densities
* Extraction of the current density, flux density, and potential
* Extraction of the terminal voltage, current, and power
* Computation of the free-space magnetic field 

**PyPEEC** has the following **limitations**:
* No capacitive effects
* No dielectric domains
* No advanced boundaries conditions
* No model order reduction techniques
* Limited to voxel geometries

The **PyPEEC** package contains the following **tools**:
* **mesher**: create a 3D voxel structure from STL or PNG files
* **viewer**: visualization of the 3D voxel structure
* **solver**: solver for the magnetic field problem
* **plotter**: visualization of the problem solution

## Project Links

* Website: https://pypeec.otvam.ch
* Repository: https://github.com/otvam/pypeec
* Releases: https://github.com/otvam/pypeec/releases
* Tags: https://github.com/otvam/pypeec/tags
* Issues: https://github.com/otvam/pypeec/issues
* PyPi: https://pypi.org/project/pypeec

## Author

* **Thomas Guillod**
* Email: guillod@otvam.ch
* Website: https://otvam.ch

## Credits

PyPEEC was created at **Dartmouth College** by the research group of **Prof. Sullivan**:
* Dartmouth College, NH, USA: https://dartmouth.edu
* Dartmouth Engineering: https://engineering.dartmouth.edu
* PMIC: https://pmic.engineering.dartmouth.edu

The FFT-accelerated PEEC method with voxels has been first described and implemented in:
* Torchio, R., IEEE TPEL, 10.1109/TPEL.2021.3092431, 2022
* Torchio, R., https://github.com/UniPD-DII-ETCOMP/FFT-PEEC

## Copyright

> (c) 2023 - Thomas Guillod - Dartmouth College
> 
>  This Source Code Form is subject to the terms of the Mozilla Public
>  License, v. 2.0. If a copy of the MPL was not distributed with this
>  file, You can obtain one at http://mozilla.org/MPL/2.0/.
