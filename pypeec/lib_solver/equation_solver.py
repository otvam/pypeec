"""
Module for checking the matrix condition number and solving a sparse equation system.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import numpy as np
import scipy.linalg as lna
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
        self.power_vec = []
        self.power_final = None
        self.power_init = None

    def get_callback_run(self, sol):
        """
        Callback displaying and saving the iteration.
        """

        # update the iteration
        self.n_iter += 1

        # get the power
        iter_tmp = self.get_n_iter()
        power_tmp = self.fct_conv(sol)

        # save the data
        self.power_vec.append(power_tmp)

        # log the results
        LOGGER.debug(f"i = {iter_tmp:d} / {power_tmp:.2e} VA")

    def get_callback_init(self, sol):
        """
        Callback for the initial solution.
        """

        # get the power
        power_tmp = self.fct_conv(sol)

        # save the data
        self.power_init = power_tmp

        # log the results
        LOGGER.debug(f"init / {power_tmp:.2e} VA")

    def get_callback_final(self, sol):
        """
        Callback for the final solution.
        """

        # get the power
        power_tmp = self.fct_conv(sol)

        # save the data
        self.power_final = power_tmp

        # log the results
        LOGGER.debug(f"final / {power_tmp:.2e} VA")

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
            "power_init": self.power_init,
            "power_final": self.power_final,
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


def _get_solver_direct(sol_init, fct_cpl, fct_sys, fct_pcd, rhs, direct_options, op_obj, iter_obj):
    """
    Solve the coupled magnetic-electric equation system with an iterative solver.
    """

    # extract
    (rhs_c, rhs_m) = rhs
    (fct_cpl_c, fct_cpl_m) = fct_cpl
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
        rhs_c = fct_sys_c(sol_c)+fct_cpl_c(sol_m)
        rhs_m = fct_sys_m(sol_m)+fct_cpl_m(sol_c)

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
    (status, sol) = matrix_iterative.get_solve(sol_init, op_sys, op_pcd, rhs, fct_callback, direct_options)

    # get residuum
    res = op_sys(sol)-rhs

    return status, sol, res


def _get_solver_domain(sol_init, sol_other, fct_cpl, fct_sys, fct_pcd, rhs, iter_options, op_obj):
    """
    Solve the electric or magnetic equation system with an iterative solver.
    """

    # get problem size
    n_dof = len(rhs)

    # function describing the preconditioner
    def fct_pcd_dom(rhs):
        return fct_pcd(rhs)

    # function describing the equation system
    def fct_sys_dom(sol):
        return fct_sys(sol)

    # get operator
    op_pcd = op_obj.get_fct_pcd(fct_pcd_dom, n_dof)
    op_sys = op_obj.get_fct_sys(fct_sys_dom, n_dof)

    # add coupling
    rhs_cpl = rhs-fct_cpl(sol_other)

    # get callback
    fct_callback = None

    # call the solver
    (status, sol) = matrix_iterative.get_solve(sol_init, op_sys, op_pcd, rhs_cpl, fct_callback, iter_options)

    return status, sol


def _get_solver_segregated(sol_init, fct_cpl, fct_sys, fct_pcd, rhs, segregated_options, op_obj, iter_obj):
    """
    Solve the segregated magnetic-electric equation system with an iterative solver.
    """

    # extract
    rel_tol = segregated_options["rel_tol"]
    abs_tol = segregated_options["abs_tol"]
    n_min = segregated_options["n_min"]
    n_max = segregated_options["n_max"]
    relax_electric = segregated_options["relax_electric"]
    relax_magnetic = segregated_options["relax_magnetic"]
    iter_electric_options = segregated_options["iter_electric_options"]
    iter_magnetic_options = segregated_options["iter_magnetic_options"]

    # extract
    (rhs_c, rhs_m) = rhs
    (fct_cpl_c, fct_cpl_m) = fct_cpl
    (fct_sys_c, fct_sys_m) = fct_sys
    (fct_pcd_c, fct_pcd_m) = fct_pcd

    # get problem size
    n_dof_c = len(rhs_c)
    n_dof_m = len(rhs_m)

    # split initial solution
    sol_c = sol_init[0:n_dof_c]
    sol_m = sol_init[n_dof_c:n_dof_c+n_dof_m]

    # init
    converged = False
    status = None
    sol = None
    res = None

    # solve
    while not converged:
        # solve and relax the electric equation systems
        (status_c, sol_c_new) = _get_solver_domain(sol_c, sol_m, fct_cpl_c, fct_sys_c, fct_pcd_c, rhs_c, iter_electric_options, op_obj)
        sol_c = (1-relax_electric)*sol_c+relax_electric*sol_c_new

        # solve and relax the magnetic equation systems
        (status_m, sol_m_new) = _get_solver_domain(sol_m, sol_c, fct_cpl_m, fct_sys_m, fct_pcd_m, rhs_m, iter_magnetic_options, op_obj)
        sol_m = (1-relax_magnetic)*sol_m+relax_magnetic*sol_m_new

        # get residuum
        res_c = fct_sys_c(sol_c)+fct_cpl_c(sol_m)-rhs_c
        res_m = fct_sys_m(sol_m)+fct_cpl_m(sol_c)-rhs_m

        # aggregate the results
        sol = np.concatenate((sol_c, sol_m))
        res = np.concatenate((res_c, res_m))
        rhs = np.concatenate((rhs_c, rhs_m))

        # run callback
        iter_obj.get_callback_run(sol)
        n_iter = iter_obj.get_n_iter()

        # check status
        status_res = lna.norm(res) <= np.maximum(rel_tol*lna.norm(rhs), abs_tol)
        status = status_c and status_m and status_res

        # check convergence
        if (n_iter > n_max) or (status and (n_iter >= n_min)):
            converged = True

    return status, sol, res


def get_solver(sol_init, fct_cpl, fct_sys, fct_pcd, rhs, fct_conv, solver_options):
    """
    Solve the equation system with an iterative solver.
    The equation system and the preconditioner are described with linear operator.
    """

    # get the condition options
    check = solver_options["check"]
    tolerance = solver_options["tolerance"]
    coupling = solver_options["coupling"]
    segregated_options = solver_options["segregated_options"]
    direct_options = solver_options["direct_options"]

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
        # first callback with the solution
        iter_obj.get_callback_init(sol_init)

        # solve the equation system
        if coupling == "direct":
            (status, sol, res) = _get_solver_direct(
                sol_init,
                fct_cpl, fct_sys, fct_pcd,
                rhs,
                direct_options,
                op_obj, iter_obj,
            )
        elif coupling == "segregated":
            (status, sol, res) = _get_solver_segregated(
                sol_init,
                fct_cpl, fct_sys, fct_pcd,
                rhs,
                segregated_options,
                op_obj, iter_obj,
            )
        else:
            raise ValueError("invalid coupling method")

        # final callback with the solution
        iter_obj.get_callback_final(sol)

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
    tolerance_electric = conditions_options["tolerance_electric"]
    tolerance_magnetic = conditions_options["tolerance_magnetic"]
    norm_options = conditions_options["norm_options"]

    # check the condition
    if check:
        cond_electric = matrix_condition.get_condition_matrix("electric", S_mat_c, norm_options)
        cond_magnetic = matrix_condition.get_condition_matrix("magnetic", S_mat_m, norm_options)
        status = (cond_electric < tolerance_electric) and (cond_magnetic < tolerance_magnetic)
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
