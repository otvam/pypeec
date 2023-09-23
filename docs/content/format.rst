File Formats
============

PyPEEC Workflow
---------------

.. figure:: ../images/workflow.png

   Description of the PyPEEC workflow (mesher, viewer, solver, and plotter).
   The input and output files of the different tools are shown.
   Additionally, a global configuration file is used.

Geometry File Format
--------------------

The ``file_geometry`` file format is used by the mesher.
This file contains the definition of the voxel structure.

.. literalinclude:: ../format/file_geometry.yaml
   :language: yaml

Definition from Index Arrays
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../format/file_geometry_voxel.yaml
   :language: yaml

Definition from 2D Vector Shapes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../format/file_geometry_shape.yaml
   :language: yaml

Definition from PNG Files
^^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../format/file_geometry_png.yaml
   :language: yaml

Definition from STL Files
^^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../format/file_geometry_stl.yaml
   :language: yaml

Problem File Format
-------------------

The ``file_problem`` file format is used by the solver.
This file contains the definition of the magnetic problem to be solved.

.. literalinclude:: ../format/file_problem.yaml
   :language: yaml

Point File Format
-----------------

The ``file_point`` file format is used by the viewer and plotter.
This file contains the definition of the points used for magnetic field evaluation.

.. literalinclude:: ../format/file_point.yaml
   :language: yaml

Other File Formats
------------------

* The configuration file format is documented in ``pypeec/data/config.yaml``.
* The ``file_tolerance`` format is documented in ``examples/config/tolerance.yaml``.
* The ``file_viewer`` format is documented in ``examples/config/viewer.yaml``.
* The ``file_plotter`` format is documented in ``examples/config/plotter.yaml``.
