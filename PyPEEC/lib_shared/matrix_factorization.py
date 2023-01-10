"""
Module for factorizing sparse matrix.
This module is used as a common interface for different solvers:
    - SuperLU: built-in library (with SciPy)
    - UMFPACK: extra library (with SciKits)

SuperLU is available on all platforms and easy to install.
UMFPACK need to be compiled (easy on Linux, difficult on other platforms).
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import warnings
import PyPEEC.config as config

# get config
MATRIX_FACTORIZATION = config.MATRIX_FACTORIZATION

# import the right library
if MATRIX_FACTORIZATION == "SuperLU":
    import scipy.sparse.linalg as sla
    warnings.filterwarnings('ignore', module="scipy.sparse.linalg")
elif MATRIX_FACTORIZATION == "UMFPACK":
    import scikits.umfpack as umf
    warnings.filterwarnings('ignore', module="scikits.umfpack")
else:
    raise ValueError("invalid matrix factorization library")


class MatrixFactorization:
    """
    Simple class for factorizing and solving sparse matrices.
    """

    def __init__(self, A):
        """
        Constructor.
        Factorize the sparse matrix.
        """

        try:
            if MATRIX_FACTORIZATION == "SuperLU":
                self.status = True
                self.factor = sla.splu(A)
            elif MATRIX_FACTORIZATION == "UMFPACK":
                self.status = True
                self.factor = umf.splu(A)
            else:
                raise ValueError("invalid matrix factorization library")
        except RuntimeError:
            self.status = False
            self.factor = None

    def get_status(self):
        """
        Get if the matrix factorization is successful.
        """

        return self.status

    def get_solution(self, rhs):
        """
        Solve an equation system with the factorization.
        """

        if self.status:
            if MATRIX_FACTORIZATION == "SuperLU":
                sol = self.factor.solve(rhs)
            elif MATRIX_FACTORIZATION == "UMFPACK":
                sol = self.factor.solve(rhs)
            else:
                raise ValueError("invalid matrix factorization library")
        else:
            sol = None

        return sol
