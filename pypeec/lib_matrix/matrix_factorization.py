"""
Module for factorizing sparse matrices and solving equation systems.

This module is used as a common interface for different matrix solvers:
    - SuperLU is typically slower but is always available (integrated with SciPy).
    - PARDISO is typically faster than SuperLU (available through Pydiso).
    - PyAMG is typically slow but uses less memory (risk of convergence issues).
    - Identity is a using an identity matrix as preconditioner (only for debugging).

This module is only importing the required matrix solver.
This means that the unused matrix solvers are not required.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import os
import warnings
import scilogger
import numpy as np
import scipy.sparse as sps

# get a logger
LOGGER = scilogger.get_logger(__name__, "pypeec")


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
            (solver, _) = lib.adaptive_sa_solver(mat)
        else:
            raise ValueError("invalid AMF solver name")
    except Warning:
        raise RuntimeError("invalid factorization: PyAMG") from None

    # matrix solver
    def factor(rhs):
        sol = solver.solve(rhs, tol=tol, accel=krylov)
        return sol

    return factor


def _get_fact_dummy():
    """
    Dummy factorization with a diagonal matrix.
    """

    def factor(rhs):
        return rhs

    return factor


def _get_factorize_sub(mat, library, pyamg_options, pardiso_options):
    """
    Factorize a sparse matrix (main function).
    """

    # check shape
    nnz = mat.size
    (nx, ny) = mat.shape

    # display
    LOGGER.debug("matrix / size = (%d, %d)", nx, ny)
    LOGGER.debug("matrix / sparsity = %d", nnz)

    # check if the matrix is empty
    if (nx, ny) == (0, 0):
        return _get_fact_dummy()

    # factorize the matrix
    LOGGER.debug("compute factorization")
    if library == "SuperLU":
        fct = _get_fact_superlu(mat)
    elif library == "PARDISO":
        fct = _get_fact_pardiso(pardiso_options, mat)
    elif library == "PyAMG":
        fct = _get_fact_pyamg(pyamg_options, mat)
    elif library == "Identity":
        fct = _get_fact_dummy()
    else:
        raise ValueError("invalid factorization library")

    # display the status
    LOGGER.debug("factorization success")

    return fct


def _get_schur_extract(mat_11, mat_22, mat_12, mat_21):
    """
    Compute the Schur complement (with respect to the diagonal matrix).
    """

    mat_diag = sps.diags(1 / mat_11.diagonal(), format="csc")
    mat_fact = mat_22 - mat_21 * mat_diag * mat_12

    return mat_fact, mat_diag


def _get_schur_solve(fct_fact, mat_diag, mat_12, mat_21):
    """
    Solve the equation system with the Schur complement.
    """

    # split the system (Schur complement split)
    (n_schur, n_schur) = mat_diag.shape

    # function for solving the Schur complement
    def solve(rhs):
        # split the rhs vector
        rhs_a = rhs[:n_schur]
        rhs_b = rhs[n_schur:]

        # solve the equation system (Schur complement and matrix factorization)
        sol_b = fct_fact(rhs_b - (mat_21 * (mat_diag * rhs_a)))
        sol_a = mat_diag * (rhs_a - (mat_12 * sol_b))

        # assemble the solution
        sol = np.concatenate((sol_a, sol_b))

        return sol

    return solve


def get_factorize(mat, factorization_options):
    """
    Factorize a sparse matrix (with or without Schur complement).
    """

    # extract the data
    mat_11 = mat["mat_11"]
    mat_22 = mat["mat_22"]
    mat_12 = mat["mat_12"]
    mat_21 = mat["mat_21"]

    # get the options
    schur = factorization_options["schur"]
    library = factorization_options["library"]
    pyamg_options = factorization_options["pyamg_options"]
    pardiso_options = factorization_options["pardiso_options"]

    # factorize the matrix
    if schur:
        (mat_fact, mat_diag) = _get_schur_extract(mat_11, mat_22, mat_12, mat_21)
        fct_fact = _get_factorize_sub(mat_fact, library, pyamg_options, pardiso_options)
        fct_sol = _get_schur_solve(fct_fact, mat_diag, mat_12, mat_21)
    else:
        mat_fact = sps.bmat([[mat_11, mat_12], [mat_21, mat_22]], format="csc")
        fct_sol = _get_factorize_sub(mat_fact, library, pyamg_options, pardiso_options)

    return fct_sol, mat_fact
