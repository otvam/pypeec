# PyPEEC - Technical Details

## Dependencies

PyPEEC is entirely programmed in Python and is using the following packages:
* Python 3
* NumPy and SciPy
* scikit-umfpack (for the solver, optional)
* pyFFTW (for the solver, optional)
* PyVista and Pillow (for the mesher)
* Matplotlib, PyVista, PyVistaQt, QtPy, PyQt5 (for the viewer and plotter)

PyPEEC is tested on Linux x64 but should run on other platforms.
The optional UMFPACK solver is known to be difficult to install on MS Windows.
The interactions between Qt/PyVista/Matplotlib are likely be sensitive to the environment.

## Packaging and Environment

* A Python package can be built from the `pyproject.toml` and `setup.cfg` files.
* In order to create a Python Virtual Environment, use `requirements.txt`.
* In order to create a Conda Environment, use `conda.yml`.

## Tests

* The tests are located in the `tests` folder (using the `unittest` framework).
* Only integration tests currently exist (no unit tests).
* The tests are using the Python .
