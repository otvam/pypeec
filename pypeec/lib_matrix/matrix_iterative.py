"""
Module for solving a dense equation system with GMRES or GCROT.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import scipy.sparse.linalg as sla


def get_solve(sol_init, op_sys, op_pcd, rhs, fct_callback, iter_options):
    """
    Solve a sparse equation system with GMRES or GCROT (main function).
    The equation system and the preconditioner are described with linear operator.
    """

    # get the options
    solver = iter_options["solver"]
    rel_tol = iter_options["rel_tol"]
    abs_tol = iter_options["abs_tol"]
    n_inner = iter_options["n_inner"]
    n_outer = iter_options["n_outer"]

    # call the solver
    if solver == "gmres":
        (sol, flag) = sla.gmres(
            op_sys,
            rhs,
            M=op_pcd,
            x0=sol_init,
            rtol=rel_tol,
            atol=abs_tol,
            restart=n_inner,
            maxiter=n_outer,
            callback=fct_callback,
            callback_type="x",
        )
    elif solver == "gcrot":
        (sol, flag) = sla.gcrotmk(
            op_sys,
            rhs,
            M=op_pcd,
            x0=sol_init,
            rtol=rel_tol,
            atol=abs_tol,
            m=n_inner,
            maxiter=n_outer,
            callback=fct_callback,
        )
    else:
        raise ValueError("invalid matrix solver")

    # check for convergence
    status = flag == 0

    return status, sol
