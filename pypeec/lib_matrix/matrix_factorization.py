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

import warnings
from pypeec.lib_utils import timelogger
from pypeec import config

# get a logger
logger = timelogger.get_logger("FACTOR")

# get config
NP_TYPES = config.NP_TYPES


def _get_fact_superlu(mat):
    """
    Factorize a matrix with SuperLU.
    """

    # import the SciPy SuperLU library
    from scipy.sparse import linalg

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


def _get_fact_pardiso(algorithm_options, mat):
    """
    Factorize a matrix with PARDISO.
    """

    # import the UMFPACK binding
    from pydiso import mkl_solver
    from pydiso.mkl_solver import MKLPardisoSolver
    from pydiso.mkl_solver import PardisoError

    # get the options
    thread_pardiso = algorithm_options["thread_pardiso"]
    thread_mkl = algorithm_options["thread_mkl"]

    # set number of threads
    mkl_solver.set_mkl_pardiso_threads(thread_pardiso)
    mkl_solver.set_mkl_threads(thread_mkl)

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

    # import the UMFPACK binding
    from scikits import umfpack

    # prevent problematic matrices to trigger warnings
    warnings.filterwarnings("error", module="scikits.umfpack")

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


def _get_fact_iter(library, algorithm_options, mat):
    """
    Factorize a matrix with iterative method.
    """

    # import the SciPy SuperLU library
    from scipy.sparse import linalg

    # get the options
    rel_tol = algorithm_options["rel_tol"]
    abs_tol = algorithm_options["abs_tol"]
    n_iter_max = algorithm_options["n_iter_max"]

    # get the solver
    if library == "GCROT":
        solver = linalg.gcrotmk
    elif library == "BICG":
        solver = linalg.bicg
    elif library == "GMRES":
        solver = linalg.gmres
    else:
        raise ValueError("invalid matrix factorization library")

    # factorize the matrix
    def factor(rhs):
        (sol, flag) = solver(mat, rhs, tol=rel_tol, atol=abs_tol, maxiter=n_iter_max)
        return sol

    return factor


def get_factorize(mat, factorization_options):
    """
    Factorize a sparse matrix.
    """

    # extract the options
    library = factorization_options["library"]
    algorithm_options = factorization_options["algorithm_options"]

    # check shape
    nnz = mat.size
    (nx, ny) = mat.shape

    # check if the matrix is empty
    if (nx, ny) == (0, 0):
        return _get_fact_superlu(mat)

    # compute matrix density
    density = nnz/(nx*ny)

    # display
    logger.debug("matrix size: (%d, %d)" % (nx, ny))
    logger.debug("matrix elements: %d" % nnz)
    logger.debug("matrix density: %.3e" % density)
    logger.debug("matrix library: %s" % library)

    # factorize the matrix
    logger.debug("matrix factorization")

    if library == "SuperLU":
        factor = _get_fact_superlu(mat)
    elif library == "UMFPACK":
        factor = _get_fact_umfpack(mat)
    elif library == "PARDISO":
        factor = _get_fact_pardiso(algorithm_options, mat)
    elif library in ["GCROT", "BICG", "GMRES"]:
        factor = _get_fact_iter(library, algorithm_options, mat)
    else:
        raise ValueError("invalid matrix factorization library")

    if factor is None:
        logger.warning("factorization failure")
    else:
        logger.debug("factorization success")

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
