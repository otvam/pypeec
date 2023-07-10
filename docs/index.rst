PyPEEC - 3D PEEC Solver
=======================

.. toctree::
   :maxdepth: 0
   :hidden:

   Home <self>
   content/about
   content/gallery
   content/tutorial
   content/examples
   content/technical
   content/format
   api/api

.. image:: images/banner.png
  :alt: PyPEEC Banner

.. Important::
    * **Website:** `pypeec.otvam.ch <https://pypeec.otvam.ch>`_
    * **Repository:** `github.com/otvam/pypeec <https://github.com/otvam/pypeec>`_

**PyPEEC** is a **3D quasi-magnetostatic field solver** with the following characteristics:

* **PEEC method** with **FFT acceleration**
* Representation of the **geometry** with **3D voxels**
* **Multithreading and GPU acceleration** are available
* **Fast** with **moderate memory** requirements
* Import the **geometry** from **STL**, **PNG**, and **GERBER** files
* Draw the **geometry** with stacked 2D **vector shapes** or **voxel indices**
* **Pure Python** and **Open source** implementation
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

The **PyPEEC** package contains the following tools:

* **mesher**: create a 3D voxel structure from STL or PNG files
* **viewer**: visualization of the 3D voxel structure
* **solver**: solver for the magnetic field problem
* **plotter**: visualization of the problem solution
