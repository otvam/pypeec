"""
Module for factorizing sparse matrix.

This module is used as a common interface for different solvers:
    - SuperLU is typically slower but is always available (integrated with SciPy)
    - UMFPACK is typically faster than SuperLU (available through SciKits)
    - PARDISO is typically faster than UMFPACK (available through Pydiso)
#   - IDENTITY is using the identity matrix as a solution (for debug)

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

# get factorization config
FACTORIZATION_LIBRARY = config.FACTORIZATION_LIBRARY
THREAD_PARDISO = config.FACTORIZATION_OPTIONS.THREAD_PARDISO
THREAD_MKL = config.FACTORIZATION_OPTIONS.THREAD_MKL

# find the number of threads
if THREAD_PARDISO is None:
    THREAD_PARDISO = os.cpu_count()
if THREAD_MKL is None:
    THREAD_MKL = os.cpu_count()

# import the right library
if FACTORIZATION_LIBRARY == "SuperLU":
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
elif FACTORIZATION_LIBRARY == "IDENTITY":
    pass
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


def _get_factorize_sub(mat):
    """
    Factorize a sparse matrix (main function).
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
    LOGGER.debug("matrix size: (%d, %d)" % (nx, ny))
    LOGGER.debug("matrix elements: %d" % nnz)
    LOGGER.debug("matrix density: %.2e" % density)
    LOGGER.debug("library: %s" % FACTORIZATION_LIBRARY)

    # factorize the matrix
    LOGGER.debug("compute factorization")
    if FACTORIZATION_LIBRARY == "SuperLU":
        factor = _get_fact_superlu(mat)
    elif FACTORIZATION_LIBRARY == "UMFPACK":
        factor = _get_fact_umfpack(mat)
    elif FACTORIZATION_LIBRARY == "PARDISO":
        factor = _get_fact_pardiso(mat)
    elif FACTORIZATION_LIBRARY == "IDENTITY":
        factor = factor_empty
    else:
        raise ValueError("invalid matrix factorization library")

    # display the status
    if factor is None:
        LOGGER.warning("factorization failure")
    else:
        LOGGER.debug("factorization success")

    return factor


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
