"""
Module for factorizing sparse matrix.
This module is used as a common interface for different solvers:
    - SuperLU: built-in library (with SciPy)
    - UMFPACK: extra library (with SciKits)

SuperLU is available on all platforms and easy to install.
UMFPACK need to be installed (and often compiled).

WARNING: UMFPACK is difficult to install on MS Windows.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import warnings
from PyPEEC import config
from PyPEEC.lib_utils import timelogger

# get a logger
logger = timelogger.get_logger("FACTOR")

# get config
MATRIX_FACTORIZATION = config.MATRIX_FACTORIZATION

# import the right library
if MATRIX_FACTORIZATION == "SuperLU":
    import scipy.sparse.linalg as sla
elif MATRIX_FACTORIZATION == "UMFPACK":
    import scikits.umfpack as umf
else:
    raise ValueError("invalid matrix factorization library")

# prevent problematic matrices to trigger warnings
warnings.filterwarnings("ignore", module="scipy.sparse.linalg")
warnings.filterwarnings("ignore", module="scikits.umfpack")

def get_factorize(mat):
    """
    Factorize a sparse matrix.
    """

    # check shape
    nnz = mat.size
    (nx, ny) = mat.shape

    # check if the matrix is empty
    if (nx, ny) == (0, 0):
        return sla.splu(mat)

    # display
    logger.debug("matrix size: (%d, %d) / %d" % (nx, ny, nnz))

    # factorize the matrix
    try:
        logger.debug("matrix factorization")

        if MATRIX_FACTORIZATION == "SuperLU":
            factor = sla.splu(mat)
        elif MATRIX_FACTORIZATION == "UMFPACK":
            factor = umf.splu(mat)
        else:
            raise ValueError("invalid matrix factorization library")

        logger.debug("factorization success")
    except RuntimeError:
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
    if MATRIX_FACTORIZATION == "SuperLU":
        sol = factor.solve(rhs)
    elif MATRIX_FACTORIZATION == "UMFPACK":
        sol = factor.solve(rhs)
    else:
        raise ValueError("invalid matrix factorization library")

    return sol
