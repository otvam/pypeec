PyPEEC - 3D PEEC Solver
=======================

.. toctree::
   :caption: General Doc
   :maxdepth: 0
   :hidden:

   Home <self>
   content/about
   content/tutorial
   content/examples
   content/gallery
   content/workflow

.. toctree::
   :caption: Technical Doc
   :maxdepth: 0
   :hidden:

   content/technical
   content/implementation
   content/warnings
   content/format
   api/index_api

.. image:: images/header.png
  :alt: PyPEEC Banner

------------

.. Important::
    * **Website:** `pypeec.otvam.ch <https://pypeec.otvam.ch>`_
    * **Repository:** `github.com/otvam/pypeec <https://github.com/otvam/pypeec>`_
    * **Package:** `pypi.org/project/pypeec <https://pypi.org/project/pypeec>`_

------------

**PyPEEC** is a **3D quasi-magnetostatic PEEC solver** developed at **Dartmouth College** within the Power Management Integration Center (PMIC).
PyPEEC is a **fast solver** (FFT and GPU accelerated) that can simulate a large variety of **magnetic components** (inductors, transformers, chokes, IPT coils, busbars, etc.).
The tool contains a **mesher** (STL, PNG, and GERBER formats), a **solver** (static and frequency domain), and **advanced plotting** capabilities.
The code is written in **Python** and is fully **open source**!

------------

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

------------

.. image:: images/footer.png
  :alt: Dartmouth PMIC
