API Doc
=======

..
   author = "Thomas Guillod"
   copyright = "Thomas Guillod - Dartmouth College"
   license = "Mozilla Public License Version 2.0"

List of Packages
----------------

=======================  =======================================================
``pypeec``               Main PyPEEC package.
``pypeec.run``           Mesher, solver, viewer, and plotter.
``pypeec.utils``         Various independent utils for data manipulation.
``pypeec.data``          Modules containing all the static data.
``pypeec.lib_check``     Library for checking the integrity of the input data.
``pypeec.lib_matrix``    Library for handling and manipulating matrices.
``pypeec.lib_plot``      Modules used by the viewer and plotter.
``pypeec.lib_mesher``    Modules used by the mesher.
``pypeec.lib_solver``    Modules used by the solver.
=======================  =======================================================

Mesher Functions
----------------

.. autofunction:: pypeec.run_mesher_data
.. autofunction:: pypeec.run_mesher_file

Viewer Functions
----------------

.. autofunction:: pypeec.run_viewer_data
.. autofunction:: pypeec.run_viewer_file

Solver Functions
----------------

.. autofunction:: pypeec.run_solver_data
.. autofunction:: pypeec.run_solver_file

Plotter Functions
-----------------

.. autofunction:: pypeec.run_plotter_data
.. autofunction:: pypeec.run_plotter_file

Other Functions
---------------

.. autofunction:: pypeec.run_extract_examples
.. autofunction:: pypeec.run_extract_documentation
.. autofunction:: pypeec.run_arguments
.. autofunction:: pypeec.run_script
