# PyPEEC - Technical Details

## Dependencies

**PyPEEC** is entirely programmed in **Python 3** and is using the following packages:
* PyYAML
* NumPy and SciPy
* scikit-umfpack (for the solver, optional)
* pyFFTW (for the solver, optional)
* PyVista and Pillow (for the mesher)
* Matplotlib, PyVista, PyVistaQt, QtPy, PyQt5 (for the viewer and plotter)

PyPEEC is tested on Linux x64 but should run on other platforms.
The optional UMFPACK solver is known to be difficult to install on MS Windows.
It should be noted that some versions of FFTW are compiled without multithreading support.
The interactions between Qt/PyVista/Matplotlib are likely be sensitive to the environment.

# Optimization

The code is reasonably optimized, leveraging NumPy and SciPy for the heavy operations.
All the code is vectorized, no loops are used for the array operations.
Sparse matrix algebra is used wherever appropriate to speed up the code and limit the memory consumption.
The optional libraries FFTW and UMFPACK can be used to speed up the solver.

However, this code is pure Python and advanced optimizations (MKL, GPU, etc.) are not implemented.
Moreover, the memory consumption is not heavily optimized (no customized garbage collection).

## Configuration

The configuration files are loaded with the following priorities:
* `pypeec.yaml` located in the current working directory
* `.pypeec.yaml` located in the current working directory
* `pypeec.yaml` located in the user home directory
* `.pypeec.yaml` located in the user home directory
* `pypeec.yaml` located in the `PyPEEC` directory (default configuration)

## Packaging and Environment

* A Python package can be built from the `pyproject.toml` and `setup.cfg` files.
* In order to create a Python Virtual Environment, use `requirements.txt`.
* In order to create a Conda Environment, use `conda.yml`.

## Tests

* The tests are located in the `tests` folder (using the `unittest` framework).
* The shell script `run_tests.sh` is used to run the tests.
* The tests are checking that the examples are running correctly.
* Only integration tests currently exist (no unit tests).

# Warnings

> **Warning**: For problems with magnetic domains, the preconditioner is not heavily optimized.
> This might lead to a very slow convergence of the matrix solver.

> **Warning**: For large problems, the code might allocate huge amounts of memory.
> This might crash your operating system.

> **Warning**: Python Pickle files are using to store the mesher and solver results.
> Pickling data is not secure. 
> Only load Pickle files that you trust.
> Do not commit the Pickle files in the Git repository.
