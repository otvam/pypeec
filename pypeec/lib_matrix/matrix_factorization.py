"""
Module for factorizing sparse matrix.

This module is used as a common interface for different solvers:
    - SuperLU is typically slower but is always available (integrated with SciPy)
    - UMFPACK is typically faster than SuperLU (available through SciKits)
    - PARDISO is typically faster than UMFPACK (available through Pydiso)
    - PyAMG is typically slow but uses less memory (risk of convergence issues)

Todo
----
    - The warning triggered by UMFPACK should be handled in a cleaner way.
    - Such warnings are triggered by ill-conditioned matrices.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import os
import warnings
from pypeec import log
from pypeec import config

# get a logger
LOGGER = log.get_logger("FACTOR")

# get config
NP_TYPES = config.NP_TYPES

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
        return None

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
    if thread_pardiso is None:
        thread_pardiso = os.cpu_count()
    if thread_mkl is None:
        thread_mkl = os.cpu_count()

    # set number of threads
    IMPORTLIB.set_mkl_pardiso_threads(thread_pardiso)
    IMPORTLIB.set_mkl_threads(thread_mkl)

    # factorize the matrix
    try:
        mat = mat.tocsr()
        mat_factor = IMPORTLIB.MKLPardisoSolver(mat, factor=True, verbose=False)
    except Warning:
        return None

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
        return None

    # matrix solver
    def factor(rhs):
        sol = solver.solve(rhs, tol=tol, accel=krylov)
        return sol

    return factor


def _get_fact_umfpack(mat):
    """
    Factorize a matrix with UMFPACK.
    """

    # double precision is required for the solver
    mat = mat.astype(NP_TYPES.DCOMPLEX)

    # factorize the matrix
    try:
        mat_factor = IMPORTLIB.splu(mat)
    except Warning:
        return None

    # matrix solver
    def factor(rhs):
        rhs = rhs.astype(NP_TYPES.DCOMPLEX)
        sol = mat_factor.solve(rhs)
        sol = sol.astype(NP_TYPES.COMPLEX)
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
    density = nnz/(nx*ny)

    # display
    LOGGER.debug("matrix size: (%d, %d)" % (nx, ny))
    LOGGER.debug("matrix elements: %d" % nnz)
    LOGGER.debug("matrix density: %.2e" % density)
    LOGGER.debug("library: %s" % LIBRARY)

    # factorize the matrix
    LOGGER.debug("compute factorization")
    if LIBRARY == "SuperLU":
        factor = _get_fact_superlu(mat)
    elif LIBRARY == "UMFPACK":
        factor = _get_fact_umfpack(mat)
    elif LIBRARY == "PARDISO":
        factor = _get_fact_pardiso(mat)
    elif LIBRARY == "PyAMG":
        factor = _get_fact_pyamg(mat)
    else:
        raise ValueError("invalid matrix factorization library")

    # display the status
    if factor is None:
        LOGGER.warning("factorization failure")
        return factor_dummy
    else:
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
    elif LIBRARY == "UMFPACK":
        import scikits.umfpack as lib_tmp
    elif LIBRARY == "PARDISO":
        import pydiso.mkl_solver as lib_tmp
    elif LIBRARY == "PyAMG":
        import pyamg.aggregation as lib_tmp
    elif LIBRARY == "none":
        lib_tmp = None
    else:
        raise ValueError("invalid factorization library")

    # assign import library to global
    global IMPORTLIB
    IMPORTLIB = lib_tmp

    # prevent problematic matrices to trigger warnings
    warnings.filterwarnings("error", module="scikits.umfpack")
    warnings.filterwarnings("error", module="pydiso.mkl_solver")


def get_factorize(name, mat):
    """
    Factorize a sparse matrix (log wrapper).
    """

    LOGGER.debug("factorization: %s" % name)
    with log.BlockIndent():
        factor = _get_factorize_sub(mat)

    return factor


def get_solve(factor, rhs):
    """
    Solve an equation system with a given factorization.
    """

    # check that the factorization is valid
    if factor is None:
        raise RuntimeError("invalid factorization")

    # solve the equation system
    sol = factor(rhs)

    return sol
