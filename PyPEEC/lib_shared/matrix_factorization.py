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
    raise ValueError("invalid matrix factorization options")


class MatrixFactorization:
    """
    Simple class for factorizing and solving sparse matrices.
    Two different methods are available:
        - SuperLU: built-in with SciPy
        - UMFPACK: extra library (with SciKits)
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
                raise ValueError("invalid matrix factorization options")
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
        Set the timer with a provided timestamp.
        """

        if self.status:
            if MATRIX_FACTORIZATION == "SuperLU":
                sol = self.factor.solve(rhs)
            elif MATRIX_FACTORIZATION == "UMFPACK":
                sol = self.factor.solve(rhs)
            else:
                raise ValueError("invalid matrix factorization options")
        else:
            sol = None

        return sol
