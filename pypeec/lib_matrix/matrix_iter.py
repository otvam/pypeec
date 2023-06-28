"""
Module for solving a sparse equation system with GMRES.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import scipy.sparse.linalg as sla
from pypeec import log

# get a logger
LOGGER = log.get_logger("GMRES")


class _IterCounter:
    """
    Simple class used as a callback to monitor the iterative solver iterations:
        - using the residuum as the callback input data
        - using the solution as the callback input data
    """

    def __init__(self, fct_conv):
        """
        Constructor.
        """

        # assign data
        self.fct_conv = fct_conv

        # init data
        self.n_iter = 0
        self.iter_vec = []
        self.P_vec = []
        self.Q_vec = []

    def get_callback_run(self, data):
        """
        Callback displaying and saving the iteration.
        """

        # update the iteration
        self.n_iter += 1
        self.iter_vec.append(self.n_iter)

        # get the power
        (P, Q) = self.fct_conv(data)

        # save the data
        self.P_vec.append(P)
        self.Q_vec.append(Q)

        # log the results
        LOGGER.debug("matrix iter: iter = %d / P = %.3e / Q = %.3e" % (self.n_iter, P, Q))

    def get_n_iter(self):
        """
        Get the number of iterations.
        """

        return self.n_iter

    def get_conv(self):
        """
        Get a summary of the convergence process.
        """

        conv = {
            "iter_vec": self.iter_vec,
            "P_vec": self.P_vec,
            "Q_vec": self.Q_vec
        }

        return conv


class _OperatorCounter:
    """
    Simple wrapper class for linear operator counting the number of evaluations.
    """

    def __init__(self, op):
        """
        Constructor.
        """

        # assign data
        self.op = op

        # init data
        self.n_eval = 0

    def get_op(self):
        """
        Get an operator that counts the number of evaluations.
        """

        def fct(x):
            self.n_eval += 1
            y = self.op(x)
            return y

        op_count = sla.LinearOperator(self.op.shape, matvec=fct, dtype=self.op.dtype)

        return op_count

    def get_n_eval(self):
        """
        Get the number of evaluations.
        """

        return self.n_eval


def get_solve(sol_init, sys_op, pcd_op, rhs, fct_conv, iter_options):
    """
    Solve a sparse equation system with GMRES.
    The equation system and the preconditioner are described with linear operator.
    """

    # get the options
    solver = iter_options["solver"]
    rel_tol = iter_options["rel_tol"]
    abs_tol = iter_options["abs_tol"]
    n_inner = iter_options["n_inner"]
    n_outer = iter_options["n_outer"]

    # init list for storing the residuum (callback)
    LOGGER.debug("enter matrix solver")

    # object for counting the solver iterations (callback)
    obj = _IterCounter(fct_conv)

    # objects for counting the operator evaluations
    sys_obj = _OperatorCounter(sys_op)
    pcd_obj = _OperatorCounter(pcd_op)
    sys_op_tmp = sys_obj.get_op()
    pcd_op_tmp = pcd_obj.get_op()

    # define callback
    def fct_callback(data):
        obj.get_callback_run(data)

    # call the solver
    if solver == "GMRES":
        (sol, flag) = sla.gmres(
            sys_op_tmp, rhs, M=pcd_op_tmp, x0=sol_init,
            tol=rel_tol, atol=abs_tol,
            restart=n_inner, maxiter=n_outer,
            callback=fct_callback, callback_type="x",
        )
    elif solver == "GCROT":
        (sol, flag) = sla.gcrotmk(
            sys_op_tmp, rhs, M=pcd_op_tmp, x0=sol_init,
            tol=rel_tol, atol=abs_tol,
            m=n_inner, maxiter=n_outer,
            callback=fct_callback,
        )
    else:
        raise ValueError("invalid matrix solver")

    # check for convergence
    status = flag == 0

    # get the number of iterations
    n_sys_eval = sys_obj.get_n_eval()
    n_pcd_eval = pcd_obj.get_n_eval()
    n_iter = obj.get_n_iter()
    conv = obj.get_conv()

    # assign results
    alg = {"n_sys_eval": n_sys_eval, "n_pcd_eval": n_pcd_eval, "n_iter": n_iter, "conv": conv}

    # exit
    LOGGER.debug("exit matrix solver")

    return status, alg, sol
