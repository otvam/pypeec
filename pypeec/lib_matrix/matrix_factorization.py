"""
Module for factorizing sparse matrices and solving equation systems.

This module is used as a common interface for different matrix solvers:
    - SuperLU is typically slower but is always available (integrated with SciPy)
    - PARDISO is typically faster than SuperLU (available through Pydiso)
    - PyAMG is typically slow but uses less memory (risk of convergence issues)

This module is only importing the required matrix solver.
This means that the unused matrix solvers are not required.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import os
import warnings
import scilogger

# get a logger
LOGGER = scilogger.get_logger(__name__, "pypeec")

# dummy options
LIBRARY = None
IMPORTLIB = None
PYAMG_OPTIONS = None
PARDISO_OPTIONS = None


def _get_fact_superlu(mat):
    """
    Factorize a matrix with SuperLU.
    """

    # factorize the matrix
    try:
        mat_factor = IMPORTLIB.splu(mat)
    except Warning:
        raise RuntimeError("invalid factorization: SuperLU") from None

    # matrix solver
    def factor(rhs):
        sol = mat_factor.solve(rhs)
        return sol

    return factor


def _get_fact_pardiso(mat):
    """
    Factorize a matrix with PARDISO.
    """

    # get options
    thread_pardiso = PARDISO_OPTIONS["thread_pardiso"]
    thread_mkl = PARDISO_OPTIONS["thread_mkl"]

    # find the number of threads
    if thread_pardiso < 0:
        thread_pardiso = os.cpu_count() + thread_pardiso + 1
    if thread_mkl < 0:
        thread_mkl = os.cpu_count() + thread_mkl + 1
    if thread_pardiso == 0:
        thread_pardiso = 1
    if thread_mkl == 0:
        thread_mkl = 1

    # set number of threads
    if thread_pardiso is not None:
        IMPORTLIB.set_mkl_pardiso_threads(thread_pardiso)
    if thread_mkl is not None:
        IMPORTLIB.set_mkl_threads(thread_mkl)

    # factorize the matrix
    try:
        mat = mat.tocsr()
        mat_factor = IMPORTLIB.MKLPardisoSolver(mat, factor=True, verbose=False)
    except Warning:
        raise RuntimeError("invalid factorization: PARDISO") from None

    # matrix solver
    def factor(rhs):
        sol = mat_factor.solve(rhs)
        return sol

    return factor


def _get_fact_pyamg(mat):
    """
    Factorize a matrix with PyAMG.
    """

    # get options
    tol = PYAMG_OPTIONS["tol"]
    solver = PYAMG_OPTIONS["solver"]
    krylov = PYAMG_OPTIONS["krylov"]

    # factorize the matrix
    try:
        mat = mat.tocsr()
        if solver == "root":
            solver = IMPORTLIB.rootnode_solver(mat)
        elif solver == "adapt":
            (solver, work) = IMPORTLIB.adaptive_sa_solver(mat)
        else:
            raise ValueError("invalid AMF solver name")
    except Warning:
        raise RuntimeError("invalid factorization: PyAMG") from None

    # matrix solver
    def factor(rhs):
        sol = solver.solve(rhs, tol=tol, accel=krylov)
        return sol

    return factor


def _get_factorize_sub(mat):
    """
    Factorize a sparse matrix (main function).
    """

    # check shape
    nnz = mat.size
    (nx, ny) = mat.shape

    # factorization for empty matrices
    def factor_dummy(rhs):
        return rhs

    # check if the matrix is empty
    if (nx, ny) == (0, 0):
        return factor_dummy

    # compute matrix density
    density = nnz / (nx * ny)

    # display
    LOGGER.debug("matrix size: (%d, %d)" % (nx, ny))
    LOGGER.debug("matrix elements: %d" % nnz)
    LOGGER.debug("matrix density: %.2e" % density)

    # factorize the matrix
    LOGGER.debug("compute factorization")
    if LIBRARY == "SuperLU":
        factor = _get_fact_superlu(mat)
    elif LIBRARY == "PARDISO":
        factor = _get_fact_pardiso(mat)
    elif LIBRARY == "PyAMG":
        factor = _get_fact_pyamg(mat)
    else:
        raise ValueError("invalid matrix factorization library")

    # display the status
    LOGGER.debug("factorization success")

    return factor


def set_options(factorization_options):
    """
    Assign the options and load the right libray.
    """

    # assign global variable
    global LIBRARY
    global PYAMG_OPTIONS
    global PARDISO_OPTIONS
    LIBRARY = factorization_options["library"]
    PYAMG_OPTIONS = factorization_options["pyamg_options"]
    PARDISO_OPTIONS = factorization_options["pardiso_options"]

    # import the right library
    if LIBRARY == "SuperLU":
        import scipy.sparse.linalg as lib_tmp
    elif LIBRARY == "PARDISO":
        import pydiso.mkl_solver as lib_tmp
    elif LIBRARY == "PyAMG":
        import pyamg.aggregation as lib_tmp
    else:
        raise ValueError("invalid factorization library")

    # assign import library to global
    global IMPORTLIB
    IMPORTLIB = lib_tmp

    # prevent problematic matrices to trigger warnings
    warnings.filterwarnings("error", module="scipy.sparse.linalg")
    warnings.filterwarnings("error", module="pyamg.aggregation")
    warnings.filterwarnings("error", module="pydiso.mkl_solver")


def get_factorize(name, mat):
    """
    Factorize a sparse matrix (log wrapper).
    """

    LOGGER.debug("factorization: %s" % name)
    with LOGGER.BlockIndent():
        factor = _get_factorize_sub(mat)

    return factor


def get_solve(factor, rhs):
    """
    Solve an equation system with a given factorization.
    """

    sol = factor(rhs)

    return sol
