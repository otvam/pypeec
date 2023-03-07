"""
Module for factorizing sparse matrix.
This module is used as a common interface for different solvers:
    - SuperLU: built-in library (with SciPy)
    - UMFPACK: extra library (with SciKits)
    - PARDISO: extra library (with Pydiso)
    - GCROT: built-in library (with SciPy)
    - BICG: built-in library (with SciPy)
    - GMRES: built-in library (with SciPy)

SuperLU is available on all platforms and easy to install.
UMFPACK and PARDISO need to be installed separately.

GCROT, BICG, and GMRES are iterative solvers and are used without preconditioner.
Therefore, these solvers are typically unstable and should only be used for particular problems.

WARNING: UMFPACK is difficult to install on MS Windows.

WARNING: PARDISO is difficult to install on MS Windows.
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
    from scipy.sparse import linalg

    # factorize the matrix
    try:
        mat_factor = linalg.splu(mat)
    except RuntimeError:
        logger.warning("factorization failure")
        return None

    # matrix solver
    def factor(rhs):
        sol = mat_factor.solve(rhs)
        return sol

    return factor


def _get_fact_pardiso(solver_options, mat):
    """
    Factorize a matrix with PARDISO.
    """

    # import the UMFPACK binding
    from pydiso import mkl_solver
    from pydiso.mkl_solver import MKLPardisoSolver
    from pydiso.mkl_solver import PardisoError

    # get the options
    thread_pardiso = solver_options["thread_pardiso"]
    thread_mkl = solver_options["thread_mkl"]

    # set number of threads
    mkl_solver.set_mkl_pardiso_threads(thread_pardiso)
    mkl_solver.set_mkl_threads(thread_mkl)

    # factorize the matrix
    try:
        mat = mat.tocsr()
        mat_factor = MKLPardisoSolver(mat, factor=True, verbose=False)
    except PardisoError:
        logger.warning("factorization failure")
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
        logger.warning("factorization failure")
        return None

    # matrix solver
    def factor(rhs):
        rhs = rhs.astype(NP_TYPES.DCOMPLEX)
        sol = mat_factor.solve(rhs)
        sol = sol.astype(NP_TYPES.COMPLEX)
        return sol

    return factor


def _get_fact_iter(library, solver_options, mat):
    """
    Factorize a matrix with iterative method.
    """

    # import the SciPy SuperLU library
    from scipy.sparse import linalg

    # get the options
    rel_tol = solver_options["rel_tol"]
    abs_tol = solver_options["abs_tol"]
    n_iter_max = solver_options["n_iter_max"]

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
        elif library == "PARDISO":
            factor = _get_fact_pardiso(solver_options, mat)
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
