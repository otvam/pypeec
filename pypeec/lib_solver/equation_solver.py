"""
Module for checking the matrix condition number and solving a sparse equation system.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import numpy as np
import scipy.sparse.linalg as sla
from pypeec.lib_matrix import matrix_condition
from pypeec.lib_matrix import matrix_iterative
from pypeec import log
from pypeec import config

# get config
NP_TYPES = config.NP_TYPES

# get a logger
LOGGER = log.get_logger("EQUATION")


class _IterCounter:
    """
    Simple class used as a callback to monitor the solver iterations.
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


class _OpCounter:
    """
    Simple class used for creating linear operators and counting the evaluations.
    """

    def __init__(self):
        """
        Constructor.
        Init the counters.
        """

        # init data
        self.n_pcd_eval = 0
        self.n_sys_eval = 0

    def get_fct_pcd(self, op, n_dof):
        """
        Get a preconditioner operator that counts the number of evaluations.
        """

        def fct(x):
            self.n_pcd_eval += 1
            y = op(x)
            return y

        op_count = sla.LinearOperator((n_dof, n_dof), matvec=fct, dtype=NP_TYPES.COMPLEX)

        return op_count

    def get_fct_sys(self, op, n_dof):
        """
        Get a system operator that counts the number of evaluations.
        """

        def fct(x):
            self.n_sys_eval += 1
            y = op(x)
            return y

        op_count = sla.LinearOperator((n_dof, n_dof), matvec=fct, dtype=NP_TYPES.COMPLEX)

        return op_count

    def get_n_pcd_eval(self):
        """
        Get the number of preconditioner evaluations.
        """

        return self.n_pcd_eval

    def get_n_sys_eval(self):
        """
        Get the number of system evaluations.
        """

        return self.n_sys_eval


def _get_solver_coupled(sol_init, fct_sys, fct_pcd, rhs, iter_options, op_obj, iter_obj):
    """
    Solve the coupled magnetic-electric equation system with an iterative solver.
    """

    # extract
    (rhs_c, rhs_m) = rhs
    (fct_sys_c, fct_sys_m) = fct_sys
    (fct_pcd_c, fct_pcd_m) = fct_pcd

    # get problem size
    n_dof_c = len(rhs_c)
    n_dof_m = len(rhs_m)

    # function describing the preconditioner
    def fct_pcd_all(rhs):
        # split vector
        rhs_c = rhs[0:n_dof_c]
        rhs_m = rhs[n_dof_c:n_dof_c+n_dof_m]

        # solve the preconditioner
        sol_c = fct_pcd_c(rhs_c)
        sol_m = fct_pcd_m(rhs_m)

        # assemble solution
        sol = np.concatenate((sol_c, sol_m))

        return sol

    # function describing the equation system
    def fct_sys_all(sol):
        # split vector
        sol_c = sol[0:n_dof_c]
        sol_m = sol[n_dof_c:n_dof_c+n_dof_m]

        # solve the system
        rhs_c = fct_sys_c(sol_c, sol_m)
        rhs_m = fct_sys_m(sol_m, sol_c)

        # assemble solution
        rhs = np.concatenate((rhs_c, rhs_m))

        return rhs

    # get operator
    op_pcd = op_obj.get_fct_pcd(fct_pcd_all, n_dof_c+n_dof_m)
    op_sys = op_obj.get_fct_sys(fct_sys_all, n_dof_c+n_dof_m)

    # get callback
    def fct_callback(sol):
        iter_obj.get_callback_run(sol)

    # assemble rhs
    rhs = np.concatenate((rhs_c, rhs_m))

    # call the solver
    (status, sol, res) = matrix_iterative.get_solve(sol_init, op_sys, op_pcd, rhs, fct_callback, iter_options)

    return status, sol, res


def get_solver(sol_init, fct_sys, fct_pcd, rhs, fct_conv, solver_options):
    """
    Solve the equation system with an iterative solver.
    The equation system and the preconditioner are described with linear operator.
    """

    # get the condition options
    check = solver_options["check"]
    tolerance = solver_options["tolerance"]
    iter_options = solver_options["iter_options"]

    # get system size
    (rhs_c, rhs_m) = rhs
    n_dof_electric = len(rhs_c)
    n_dof_magnetic = len(rhs_m)
    n_dof_total = n_dof_electric+n_dof_magnetic

    # get initial solution
    if sol_init is None:
        sol_init = np.zeros(n_dof_total, dtype=NP_TYPES.COMPLEX)

    # create operator and iter counter object
    op_obj = _OpCounter()
    iter_obj = _IterCounter(fct_conv)

    # call the solver
    LOGGER.debug("solver run")
    with log.BlockIndent():
        (status, sol, res) = _get_solver_coupled(sol_init, fct_sys, fct_pcd, rhs, iter_options, op_obj, iter_obj)

    # final callback
    iter_obj.get_callback_run(sol)

    # compute and check the residuum
    res_rms = np.sqrt(np.mean(np.abs(res)**2))

    # solver success
    if check:
        status = status and (res_rms < tolerance)
    else:
        status = True

    # extract alg results
    n_sys_eval = op_obj.get_n_sys_eval()
    n_pcd_eval = op_obj.get_n_pcd_eval()
    n_iter = iter_obj.get_n_iter()
    conv = iter_obj.get_conv()

    # assign the results
    solver_status = {
        "check": check,
        "n_dof_electric": n_dof_electric,
        "n_dof_magnetic": n_dof_magnetic,
        "n_dof_total": n_dof_total,
        "n_iter": n_iter,
        "n_sys_eval": n_sys_eval,
        "n_pcd_eval": n_pcd_eval,
        "res_rms": res_rms,
        "status": status,
    }

    # display results
    LOGGER.debug("solver summary")
    with log.BlockIndent():
        # display results
        LOGGER.debug("check = %s" % check)
        LOGGER.debug("status = %s" % status)
        LOGGER.debug("n_dof_total = %d" % n_dof_total)
        LOGGER.debug("n_dof_electric = %d" % n_dof_electric)
        LOGGER.debug("n_dof_magnetic = %d" % n_dof_magnetic)
        LOGGER.debug("n_iter = %d" % n_iter)
        LOGGER.debug("n_sys_eval = %d" % n_sys_eval)
        LOGGER.debug("n_pcd_eval = %d" % n_pcd_eval)
        LOGGER.debug("res_rms = %.2e" % res_rms)

        # display status
        if check:
            if status:
                LOGGER.debug("convergence achieved")
            else:
                LOGGER.warning("convergence issues")
        else:
            LOGGER.debug("convergence check is disabled")

    return sol, res, conv, status, solver_status


def get_condition(S_mat_c, S_mat_m, conditions_options):
    """
    Compute an estimate of the condition number (norm 1) of preconditioner Schur complements.
    The condition number is used to detect problematic (quasi-singular) systems.
    """

    # get the condition options
    check = conditions_options["check"]
    tolerance = conditions_options["tolerance"]
    norm_options = conditions_options["norm_options"]

    # check the condition
    if check:
        cond_electric = matrix_condition.get_condition_matrix("electric", S_mat_c, norm_options)
        cond_magnetic = matrix_condition.get_condition_matrix("magnetic", S_mat_m, norm_options)
        status = (cond_electric < tolerance) and (cond_magnetic < tolerance)
    else:
        cond_electric = float("nan")
        cond_magnetic = float("nan")
        status = True

    # assign the results
    condition_status = {
        "check": check,
        "cond_electric": cond_electric,
        "cond_magnetic": cond_magnetic,
        "status": status,
    }

    # display status
    LOGGER.debug("condition summary")
    with log.BlockIndent():
        LOGGER.debug("check = %s" % check)
        LOGGER.debug("status = %s" % status)
        if check:
            LOGGER.debug("cond_electric = %.2e" % cond_electric)
            LOGGER.debug("cond_magnetic = %.2e" % cond_magnetic)
            if status:
                LOGGER.debug("matrix condition is good")
            else:
                LOGGER.warning("matrix condition is problematic")
        else:
            LOGGER.debug("matrix condition check is disabled")

    return status, condition_status
