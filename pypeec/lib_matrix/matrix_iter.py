"""
Module for solving a sparse equation system with GMRES or GCROT.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import scipy.sparse.linalg as sla
from pypeec import log

# get a logger
LOGGER = log.get_logger("ITER")


class _IterCounter:
    """
    Simple class used as a callback to monitor the iterative solver iterations.
    """

    def __init__(self, fct_conv):
        """
        Constructor.
        Init the counters.
        """

        # assign data
        self.fct_conv = fct_conv

        # init data
        self.n_iter = 0
        self.iter_vec = []
        self.power_vec = []

    def get_callback_run(self, sol):
        """
        Callback displaying and saving the iteration.
        """

        # update the iteration
        self.n_iter += 1

        # add the iteration
        iter_tmp = self.get_n_iter()

        # get the power
        power_tmp = self.fct_conv(sol)

        # save the data
        self.iter_vec.append(iter_tmp)
        self.power_vec.append(power_tmp)

        # log the results
        LOGGER.debug(f"i = {iter_tmp:d} / {power_tmp:.2e} VA")

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
            "power_vec": self.power_vec,
        }

        return conv


class _OperatorCounter:
    """
    Simple wrapper class for linear operator counting the number of evaluations.
    """

    def __init__(self, op):
        """
        Constructor.
        Init the counters.
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


def _get_solve_sub(sol_init, sys_op, pcd_op, rhs, fct_conv, iter_options):
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

    # get problem size
    n_dof = len(rhs)

    # init solver
    LOGGER.debug("init solver")
    LOGGER.debug("solver: %s" % solver)
    LOGGER.debug("n_dof: %d" % n_dof)

    # object for counting the solver iterations (callback)
    obj = _IterCounter(fct_conv)

    # objects for counting the operator evaluations
    sys_obj = _OperatorCounter(sys_op)
    pcd_obj = _OperatorCounter(pcd_op)
    sys_op_tmp = sys_obj.get_op()
    pcd_op_tmp = pcd_obj.get_op()

    # define callback
    def fct_callback(sol):
        obj.get_callback_run(sol)

    # call the solver
    LOGGER.debug("call solver")
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

    return status, alg, sol


def get_solve(sol_init, sys_op, pcd_op, rhs, fct_conv, iter_options):
    """
    Solve a sparse equation system with GMRES or GCROT (log wrapper).
    """

    LOGGER.debug("matrix solver")
    with log.BlockIndent():
        data = _get_solve_sub(sol_init, sys_op, pcd_op, rhs, fct_conv, iter_options)

    return data
