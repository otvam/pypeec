"""
Module for factorizing sparse matrix.

This module is used as a common interface for different solvers:
    - SuperLU is typically slower but is always available (integrated with SciPy)
    - UMFPACK is typically faster than SuperLU (available through SciKits)
    - PARDISO is typically faster than UMFPACK (available through Pydiso)
    - GCROT is quite unstable but has low memory requirements (integrated with SciPy)
    - BICG is quite unstable but has low memory requirements (integrated with SciPy)
    - GMRES is quite unstable but has low memory requirements (integrated with SciPy)
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import os
import warnings
from pypeec import log
from pypeec import config

# get a logger
LOGGER = log.get_logger("FACTOR")

# get config
NP_TYPES = config.NP_TYPES

# get factorization config
FACTORIZATION_LIBRARY = config.FACTORIZATION_LIBRARY
ITER_REL_TOL = config.FACTORIZATION_OPTIONS.ITER_REL_TOL
ITER_ABS_TOL = config.FACTORIZATION_OPTIONS.ITER_ABS_TOL
ITER_N_MAX = config.FACTORIZATION_OPTIONS.ITER_N_MAX
THREAD_PARDISO = config.FACTORIZATION_OPTIONS.THREAD_PARDISO
THREAD_MKL = config.FACTORIZATION_OPTIONS.THREAD_MKL

# find the number of threads
if THREAD_PARDISO is None:
    THREAD_PARDISO = os.cpu_count()
if THREAD_MKL is None:
    THREAD_MKL = os.cpu_count()

# import the right library
if FACTORIZATION_LIBRARY in ["SuperLU", "GCROT", "BICG", "GMRES"]:
    from scipy.sparse import linalg
elif FACTORIZATION_LIBRARY == "UMFPACK":
    # import the UMFPACK binding
    from scikits import umfpack

    # prevent problematic matrices to trigger warnings
    warnings.filterwarnings("error", module="scikits.umfpack")
elif FACTORIZATION_LIBRARY == "PARDISO":
    # import the PARDISO binding
    from pydiso import mkl_solver
    from pydiso.mkl_solver import MKLPardisoSolver
    from pydiso.mkl_solver import PardisoError

    # set number of threads
    mkl_solver.set_mkl_pardiso_threads(THREAD_PARDISO)
    mkl_solver.set_mkl_threads(THREAD_MKL)
else:
    raise ValueError("invalid factorization library")


def _get_fact_superlu(mat):
    """
    Factorize a matrix with SuperLU.
    """

    # factorize the matrix
    try:
        mat_factor = linalg.splu(mat)
    except RuntimeError:
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

    # factorize the matrix
    try:
        mat = mat.tocsr()
        mat_factor = MKLPardisoSolver(mat, factor=True, verbose=False)
    except PardisoError:
        return None

    # matrix solver
    def factor(rhs):
        sol = mat_factor.solve(rhs)
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
        mat_factor = umfpack.splu(mat)
    except Warning:
        return None

    # matrix solver
    def factor(rhs):
        rhs = rhs.astype(NP_TYPES.DCOMPLEX)
        sol = mat_factor.solve(rhs)
        sol = sol.astype(NP_TYPES.COMPLEX)
        return sol

    return factor


def _get_fact_iter(solver, mat):
    """
    Factorize a matrix with iterative method.
    """

    # factorize the matrix
    def factor(rhs):
        (sol, flag) = solver(mat, rhs, tol=ITER_REL_TOL, atol=ITER_ABS_TOL, maxiter=ITER_N_MAX)
        return sol

    return factor


def get_factorize(name, mat):
    """
    Factorize a sparse matrix.
    """

    # check shape
    nnz = mat.size
    (nx, ny) = mat.shape

    # factorization for empty matrices
    def factor_empty(rhs):
        return rhs

    # check if the matrix is empty
    if (nx, ny) == (0, 0):
        return factor_empty

    # compute matrix density
    density = nnz/(nx*ny)

    # display
    LOGGER.debug("enter matrix factorization: %s" % name)
    LOGGER.debug("matrix size: (%d, %d)" % (nx, ny))
    LOGGER.debug("matrix elements: %d" % nnz)
    LOGGER.debug("matrix density: %.3e" % density)
    LOGGER.debug("factorization library: %s" % FACTORIZATION_LIBRARY)

    # factorize the matrix
    LOGGER.debug("compute factorization")
    if FACTORIZATION_LIBRARY == "SuperLU":
        factor = _get_fact_superlu(mat)
    elif FACTORIZATION_LIBRARY == "UMFPACK":
        factor = _get_fact_umfpack(mat)
    elif FACTORIZATION_LIBRARY == "PARDISO":
        factor = _get_fact_pardiso(mat)
    elif FACTORIZATION_LIBRARY == "GCROT":
        factor = _get_fact_iter(linalg.gcrotmk, mat)
    elif FACTORIZATION_LIBRARY == "BICG":
        factor = _get_fact_iter(linalg.bicg, mat)
    elif FACTORIZATION_LIBRARY == "GMRES":
        factor = _get_fact_iter(linalg.gmres, mat)
    else:
        raise ValueError("invalid matrix factorization library")

    # display the status
    if factor is None:
        LOGGER.warning("factorization failure")
    else:
        LOGGER.debug("factorization success")

    # exit
    LOGGER.debug("exit matrix factorization: %s" % name)

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
