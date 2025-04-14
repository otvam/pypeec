"""
Module for factorizing sparse matrices and solving equation systems.

This module is used as a common interface for different matrix solvers:
    - SuperLU is typically slower but is always available (integrated with SciPy).
    - PARDISO is typically faster than SuperLU (available through Pydiso).
    - PyAMG is typically slow but uses less memory (risk of convergence issues).
    - Diagonal is a dummy factorization (only for debugging).

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
FACTOR = None


def _get_fact_superlu(mat):
    """
    Factorize a matrix with SuperLU.
    """

    import scipy.sparse.linalg as lib

    # prevent problematic matrices to trigger warnings
    warnings.filterwarnings("error", module="scipy.sparse.linalg")

    # factorize the matrix
    try:
        mat_factor = lib.splu(mat)
    except Warning:
        raise RuntimeError("invalid factorization: SuperLU") from None

    # matrix solver
    def factor(rhs):
        sol = mat_factor.solve(rhs)
        return sol

    return factor


def _get_fact_pardiso(pardiso_options, mat):
    """
    Factorize a matrix with PARDISO.
    """

    import pydiso.mkl_solver as lib

    # prevent problematic matrices to trigger warnings
    warnings.filterwarnings("error", module="pydiso.mkl_solver")

    # get options
    thread_pardiso = pardiso_options["thread_pardiso"]
    thread_mkl = pardiso_options["thread_mkl"]

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
        lib.set_mkl_pardiso_threads(thread_pardiso)
    if thread_mkl is not None:
        lib.set_mkl_threads(thread_mkl)

    # factorize the matrix
    try:
        mat = mat.tocsr()
        mat_factor = lib.MKLPardisoSolver(mat, factor=True, verbose=False)
    except Warning:
        raise RuntimeError("invalid factorization: PARDISO") from None

    # matrix solver
    def factor(rhs):
        sol = mat_factor.solve(rhs)
        return sol

    return factor


def _get_fact_pyamg(pyamg_options, mat):
    """
    Factorize a matrix with PyAMG.
    """

    import pyamg.aggregation as lib

    # prevent problematic matrices to trigger warnings
    warnings.filterwarnings("error", module="pyamg.aggregation")

    # get options
    tol = pyamg_options["tol"]
    solver = pyamg_options["solver"]
    krylov = pyamg_options["krylov"]

    # factorize the matrix
    try:
        mat = mat.tocsr()
        if solver == "root":
            solver = lib.rootnode_solver(mat)
        elif solver == "adapt":
            (solver, work) = lib.adaptive_sa_solver(mat)
        else:
            raise ValueError("invalid AMF solver name")
    except Warning:
        raise RuntimeError("invalid factorization: PyAMG") from None

    # matrix solver
    def factor(rhs):
        sol = solver.solve(rhs, tol=tol, accel=krylov)
        return sol

    return factor


def _get_fact_diagonal():
    """
    Dummy factorization with a diagonal matrix.
    """

    def factor(rhs):
        return rhs

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
    fct = FACTOR(mat)

    # display the status
    LOGGER.debug("factorization success")

    return fct


def set_options(factorization_options):
    """
    Assign the options and load the right libray.
    """

    # get global variables
    global SCHUR
    global FACTOR

    # get/assign library parameters
    schur = factorization_options["schur"]
    library = factorization_options["library"]
    pyamg_options = factorization_options["pyamg_options"]
    pardiso_options = factorization_options["pardiso_options"]

    # define the factorization function
    if library == "SuperLU":
        def factor(mat):
            return _get_fact_superlu(mat)
    elif library == "PARDISO":
        def factor(mat):
            return _get_fact_pardiso(pardiso_options, mat)
    elif library == "PyAMG":
        def factor(mat):
            return _get_fact_pyamg(pyamg_options, mat)
    elif library == "Diagonal":
        def factor(_):
            return _get_fact_diagonal()
    else:
        raise ValueError("invalid factorization library")

    # assign the imported library
    FACTOR = factor
    SCHUR = schur


def get_factorize(name, mat):
    """
    Factorize a sparse matrix (log wrapper).
    """

    LOGGER.debug("factorization: %s" % name)
    with LOGGER.BlockIndent():
        fct = _get_factorize_sub(mat)

    return fct


def get_solve(fct, rhs):
    """
    Solve an equation system with a given factorization.
    """

    sol = fct(rhs)

    return sol
