"""
Module for factorizing sparse matrix.
This module is used as a common interface for different solvers:
    - SuperLU: built-in library (with SciPy)
    - UMFPACK: extra library (with SciKits)
    - GCROT: built-in library (with SciPy)
    - BICG: built-in library (with SciPy)
    - GMRES: built-in library (with SciPy)

SuperLU is available on all platforms and easy to install.
UMFPACK need to be installed (and often compiled).
GCROT, BICG, and GMRES are typically quite unstable.

WARNING: UMFPACK is difficult to install on MS Windows.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import warnings
from pypeec.lib_utils import timelogger
from pypeec.lib_utils import config

# get a logger
logger = timelogger.get_logger("FACTOR")

# get config
NP_TYPES = config.NP_TYPES


def _get_fact_superlu(mat):
    """
    Factorize a matrix with SuperLU.
    """

    # import the SciPy SuperLU library
    import scipy.sparse.linalg as sla

    # prevent problematic matrices to trigger warnings
    warnings.filterwarnings("error", module="scipy.sparse.linalg")

    # factorize the matrix
    mat_factor = sla.splu(mat)

    # matrix solver
    def fact(rhs):
        sol = mat_factor.solve(rhs)
        return sol

    return fact


def _get_fact_umfpack(mat):
    """
    Factorize a matrix with UMFPACK.
    """

    # import the UMFPACK binding
    import scikits.umfpack as umf

    # prevent problematic matrices to trigger warnings
    warnings.filterwarnings("error", module="scikits.umfpack")

    # double precision is required for the solver
    mat = mat.astype(NP_TYPES.DCOMPLEX)

    # factorize the matrix
    mat_factor = umf.splu(mat)

    # matrix solver
    def fact(rhs):
        sol = mat_factor.solve(rhs)
        sol = sol.astype(NP_TYPES.COMPLEX)
        return sol

    return fact


def _get_fact_iter(library, solver_options, mat):
    """
    Factorize a matrix with iterative method.
    """

    # import the SciPy SuperLU library
    import scipy.sparse.linalg as sla

    # prevent problematic matrices to trigger warnings
    warnings.filterwarnings("error", module="scipy.sparse.linalg")

    # get the options
    rel_tol = solver_options["rel_tol"]
    abs_tol = solver_options["abs_tol"]
    n_iter_max = solver_options["n_iter_max"]

    # get the solver
    if library == "GCROT":
        solver = sla.gcrotmk
    elif library == "BICG":
        solver = sla.bicg
    elif library == "GMRES":
        solver = sla.gmres
    else:
        raise ValueError("invalid matrix factorization library")

    # factorize the matrix
    def fact(rhs):
        (sol, flag) = solver(mat, rhs, tol=rel_tol, atol=abs_tol, maxiter=n_iter_max)
        return sol

    return fact


def get_factorize(mat, factorization_options):
    """
    Factorize a sparse matrix.
    """

    # extract the options
    library = factorization_options["library"]
    solver_options = factorization_options["solver_options"]

    # check shape
    nnz = mat.size
    (nx, ny) = mat.shape

    # check if the matrix is empty
    if (nx, ny) == (0, 0):
        return _get_fact_superlu(mat)

    # display
    logger.debug("matrix size: (%d, %d) / %d" % (nx, ny, nnz))
    logger.debug("matrix library: %s" % library)

    # factorize the matrix
    try:
        logger.debug("matrix factorization")

        if library == "SuperLU":
            factor = _get_fact_superlu(mat)
        elif library == "UMFPACK":
            factor = _get_fact_umfpack(mat)
        elif library in ["GCROT", "BICG", "GMRES"]:
            factor = _get_fact_iter(library, solver_options, mat)
        else:
            raise ValueError("invalid matrix factorization library")

        logger.debug("factorization success")
    except (RuntimeError, Warning):
        logger.warning("factorization failure")
        factor = None

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
