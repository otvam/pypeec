Workflow
========

..
   author = "Thomas Guillod"
   copyright = "Thomas Guillod - Dartmouth College"
   license = "Mozilla Public License Version 2.0"

PyPEEC Workflow
---------------

.. figure:: ../images/workflow.png

   Description of the PyPEEC workflow (mesher, viewer, solver, and plotter).
   The input files (geometry, problem, tolerance, plotter, and viewer) are either in JSON or YAML formats.
   The output files (voxel and solution) are either in JSON, MessagePack or Pickle formats.

PyPEEC Tools
------------

* **mesher**

  * Create the voxel structure.
  * Draw the geometry from voxel indices.
  * Create the geometry from 3D STL files.
  * Create the geometry with stacked PNG files.
  * Draw the geometry with stacked 2D vector shapes.
  * Assign different domain names to the voxels.
  * Resampling (refine) the voxel structure.
  * Construct the graph of the structure.
  * Check the integrity of the voxel structure.

* **viewer**

  * Visualization of the different domains composing the voxel structure.
  * Visualization of the connected components composing the voxel structure.
  * Comparison of the voxelized and original geometries.
  * Matrix showing the connected/adjacent domains.

* **solver**

  * Computation of the incidence matrix.
  * Computation of the Green and coupling tensors.
  * Computation of the resistance, inductance, and potential matrices.
  * Computation of the electric-magnetic coupling matrices.
  * Creation of the equation system describing the PEEC problem.
  * Extraction of a sparse pre-conditioner for the dense system.
  * Extraction of a matrix-vector linear operator for the full system.
  * Computation of the condition number of the pre-conditioner equation system.
  * Solve the equation system with the pre-conditioner and the linear operator.
  * Extract the solution (terminal voltages and currents, scalar fields, and vector fields).

* **plotter**

  * Plot the material and source description.
  * Plot the scalar and vector fields on the voxels.
  * Plot the magnetic near-field generated by the voxels.
  * Plot the solver convergence and residuum.

Entry Points and Scripts
------------------------

The entry points of the different tools are located in the ``pypeec`` module:

* Running the tools with files as input/output:

  * ``run_mesher_file`` - Run the **mesher**.
  * ``run_viewer_file`` - Run the **viewer**.
  * ``run_solver_file`` - Run the **solver**.
  * ``run_plotter_file`` - Run the **plotter**.

* Running the tools with data as input/output:

  * ``run_mesher_data`` - Run the **mesher**.
  * ``run_viewer_data`` - Run the **viewer**.
  * ``run_solver_data`` - Run the **solver**.
  * ``run_plotter_data`` - Run the **plotter**.

Additionally, a command line tool is installed with the package:

* ``pypeec --help`` - Display the command line options.
* ``pypeec --version`` - Display the version number.
* ``pypeec mesher`` - Run the **mesher**.
* ``pypeec viewer`` - Run the **viewer**.
* ``pypeec solver`` - Run the **solver**.
* ``pypeec plotter`` - Run the **plotter**.
* ``pypeec examples`` - Extract the **examples**.
* ``pypeec documentation`` - Extract the **documentation**.

Input/Output File Description
-----------------------------

The following input files (JSON or YAML format) are used:

* ``file_geometry`` - Description of the geometry.
* ``file_problem`` - Description of the magnetic problem.
* ``file_tolerance`` - Description of the solver numerical options.
* ``file_viewer`` - Options for the plots generated by the viewer.
* ``file_plotter`` - Options for the plots generated by the plotter.

The following files (JSON or Pickle format) are generated:

* ``file_voxel`` - Definition of the voxel structure.
* ``file_solution`` - Solution of the magnetic problem.

Geometry Preparation
--------------------

The following **open-source tools** can be used to generate **PNG** files:

* Interactive software: ``GIMP`` or ``Inkscape``
* Scripting software: ``ImageMagick`` or ``Pillow``

The following **open-source tools** can be used to generate **STL** files:

* Interactive software: ``FreeCAD`` or ``Blender``
* Scripting software: ``CadQuery`` or ``OpenSCAD``
* Mesh tools: ``MeshLab`` or ``MeshFix``

The following **open-source tools** can be used to generate **GERBER** files:

* Interactive software: ``KiCAD``
* Scripting software: ``gerber-writer``

The following **open-source tools** can be used to **visualize 3D VTK** files:

* Flexible and powerful: ``ParaView``
* Fast and minimalist: ``F3D``
