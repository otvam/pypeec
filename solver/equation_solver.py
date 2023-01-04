"""
Module for checking the matrix condition number and solving a sparse equation system.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import scipy.sparse.linalg as sla
import scipy.linalg as lna


class IterCounter:
    """
    Simple class used as a callback to count the number of iteration of the matrix solver.
    """

    def __init__(self):
        """
        Constructor.
        Init the number of iteration.
        """

        self.n_iter = 0

    def get_callback(self, res):
        """
        Callback increasing the iteration count.
        """

        self.n_iter += 1

    def get_n_iter(self):
        """
        Get the number of iterations.
        """

        return self.n_iter


def get_solver(sys_op, pcd_op, rhs, cond, solver_options):
    """
    Solve a sparse equation system with gmres.
    The equation system and the preconditioner are described with linear operator.
    """

    # get the solver options
    tol = solver_options["tol"]
    atol = solver_options["atol"]
    restart = solver_options["restart"]
    maxiter = solver_options["maxiter"]
    condmax = solver_options["condmax"]

    # object for counting the solver iterations (callback)
    obj = IterCounter()

    # define callback
    def fct(res_iter):
        obj.get_callback(res_iter)

    # call the solver
    (sol, flag) = sla.gmres(sys_op, rhs, tol=tol, atol=atol, restart=restart, maxiter=maxiter, M=pcd_op, callback=fct)

    # get the number of iterations
    n_iter = obj.get_n_iter()

    # compute the absolute and relative residuum
    res = sys_op(sol)-rhs
    res_abs = lna.norm(res)
    res_rel = lna.norm(res)/lna.norm(rhs)

    # get problem size
    n_dof = len(rhs)

    # check for convergence
    cond_ok = cond < condmax
    solver_ok = flag == 0
    has_converged = cond_ok and solver_ok

    # assign the results
    solver_status = {
        "n_iter": n_iter,
        "res_abs": res_abs,
        "res_rel": res_rel,
        "cond": cond,
        "n_dof": n_dof,
        "cond_ok": cond_ok,
        "solver_ok": solver_ok,
    }

    return sol, has_converged, solver_status


def get_condition(mat):
    """
    Compute an estimate of the condition number (norm 1) of a sparse matrix.
    """

    # compute the LU decomposition
    try:
        LU_decomposition = sla.splu(mat)
    except RuntimeError:
        return float('inf')

    # get the function for the linear operator (original matrix)
    def fct_matvec(v):
        return LU_decomposition.solve(v, trans="N")

    # get the function for the linear operator (transposed matrix)
    def fct_rmatvec(v):
        return LU_decomposition.solve(v, trans="H")

    # assign linear operator for inversion
    op = sla.LinearOperator(mat.shape, matvec=fct_matvec, rmatvec=fct_rmatvec)

    # compute the norm of the matrix inverse (estimate)
    nrm_inv = sla.onenormest(op)

    # compute the norm of the matrix (estimate)
    nrm_ori = sla.onenormest(mat)

    # compute an estimate of the condition
    cond = nrm_ori*nrm_inv

    return cond
