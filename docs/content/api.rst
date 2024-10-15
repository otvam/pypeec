API Doc
=======

.. currentmodule:: pypeec

Main Packages
-------------

============================  =====================================================
``pypeec``                    Main PyPEEC package.
``pypeec.run``                Mesher, solver, viewer, and plotter.
``pypeec.utils``              Various independent utils for data manipulation.
``pypeec.lib_check``          Library for checking the integrity of the input data.
``pypeec.lib_matrix``         Library for handling and manipulating matrices.
``pypeec.lib_mesher``         Modules used by the mesher.
``pypeec.lib_solver``         Modules used by the solver.
``pypeec.lib_visualization``  Modules used by the viewer and plotter.
``pypeec.data``               Modules containing the static data.
============================  =====================================================

Mesher Function
---------------

.. autofunction:: run_mesher_data
.. autofunction:: run_mesher_file

Viewer Function
---------------

.. autofunction:: run_viewer_data
.. autofunction:: run_viewer_file

Solver Function
---------------

.. autofunction:: run_solver_data
.. autofunction:: run_solver_file

Plotter Function
----------------

.. autofunction:: run_plotter_data
.. autofunction:: run_plotter_file

Command Line
------------

.. autofunction:: run_arguments
.. autofunction:: run_script
