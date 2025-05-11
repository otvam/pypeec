# PyPEEC - 3D Quasi-Magnetostatic Solver

---
* **Website: [pypeec.otvam.ch](https://pypeec.otvam.ch)**
* **Repository: [github.com/otvam/pypeec](https://github.com/otvam/pypeec)**
* **Conda: [anaconda.org/conda-forge/pypeec](https://anaconda.org/conda-forge/pypeec)**
* **PyPI: [pypi.org/project/pypeec](https://pypi.org/project/pypeec)**
---

## Summary

**PyPEEC** is a **3D quasi-magnetostatic PEEC solver** developed at **Dartmouth College** within the Power Management Integration Center (PMIC). 
PyPEEC is a **fast solver** (FFT and GPU accelerated) that can simulate a large variety of **magnetic components** (inductors, transformers, chokes, IPT coils, busbars, etc.). 
The tool contains a **mesher** (STL, PNG, and GERBER formats), a **solver** (static and frequency domain), and **advanced plotting** capabilities.
The code is written in **Python** and is fully **open source**!

## Capabilities

**PyPEEC** features the following **characteristics**:

* **PEEC method** with **FFT acceleration**.
* **Fast** with **moderate memory** requirements.
* Representation of the **geometry** with **3D voxels**.
* **Parallel processing** and **GPU acceleration** are available.
* Import the **geometry** from **STL**, **PNG**, and **GERBER** files.
* Draw the **geometry** with stacked 2D **vector shapes** or **voxel indices**.
* **Pure Python** and **open source** implementation.
* Can be used from the **command line** or with an **API**.
* Advanced **plotting and visualization** capabilities.
* Compatible with **Jupyter notebooks**.
* Compatible with **ParaView**.

**PyPEEC** solves the following **3D quasi-magnetostatic problems**:

* Frequency domain solution (DC and AC).
* Conductive and magnetic domains (ideal or lossy).
* Isotropic, anisotropic, lumped, and distributed materials.
* Connection of current and voltage sources.
* Extraction of the current density, flux density, and potential.
* Extraction of the terminal voltage, current, and power.
* Computation of the free-space magnetic field .

**PyPEEC** has the following **limitations**:

* No capacitive effects.
* No dielectric domains.
* No force computations.
* No advanced boundary conditions.
* No domain decomposition techniques.
* No hierarchical matrix techniques.
* No model order reduction techniques.
* Limited to voxel geometries.

The **PyPEEC** package contains the following **tools**:

* **mesher** - Create a 3D voxel structure from the geometry.
* **viewer** - Visualization of the 3D voxel structure.
* **solver** - Solve the quasi-magnetostatic problem.
* **plotter** - Visualization of the problem solution.

## Warning

The geometry is meshed with a **regular voxel structure** (uniform grid).
Some geometries/problems are not suited for voxel structures (inefficient meshing).
For such cases, PyPEEC can be very slow and consume a lot of memory.

## Project Links

* **PyPEEC**

  * [Website](https://pypeec.otvam.ch)
  * [Repository](https://github.com/otvam/pypeec)
  * [Issues](https://github.com/otvam/pypeec/issues)

* **Releases**

  * [PyPI](https://pypi.org/project/pypeec)
  * [Conda](https://anaconda.org/conda-forge/pypeec)
  * [GitHub](https://github.com/otvam/pypeec/releases)
  * [Zenodo](https://doi.org/10.5281/zenodo.14941571)

* **Documentation**

  * [Installation](https://pypeec.otvam.ch/content/install.html)
  * [Tutorial](https://pypeec.otvam.ch/content/tutorial.html)
  * [Examples](https://pypeec.otvam.ch/content/examples.html)
  * [Gallery](https://pypeec.otvam.ch/content/gallery.html)

## Author

* Name: **Thomas Guillod**
* Affiliation: Dartmouth College
* Email: guillod@otvam.ch
* Website: https://otvam.ch

## Credits

PyPEEC was created at **Dartmouth College** by the research group of **Prof. Sullivan**:

* Dartmouth College, NH, USA: https://dartmouth.edu
* Dartmouth Engineering: https://engineering.dartmouth.edu
* NSF/PMIC: https://pmic.engineering.dartmouth.edu

The FFT-accelerated PEEC method with voxels has been first described and implemented in:

* Torchio, R., IEEE TPEL, 10.1109/TPEL.2021.3092431, 2022
* Torchio, R., https://github.com/UniPD-DII-ETCOMP/FFT-PEEC

## Copyright

(c) 2023-2025 / Thomas Guillod / Dartmouth College

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

In order to facilitate the redistribution, this source code is
multi-licensed under the following additional licenses:
LGPLv2, LGPLv3, GPLv2, and GPLv3.

---

