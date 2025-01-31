"""
Module for checking the matrix condition number and solving the equation system.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import scilogger
import numpy as np
import scipy.linalg as lna
import scipy.sparse.linalg as sla
from pypeec.lib_matrix import matrix_condition
from pypeec.lib_matrix import matrix_iterative

# get a logger
LOGGER = scilogger.get_logger(__name__, "pypeec")


class PowerConvergenceError(RuntimeError):
    """
    Simple exception for signaling the convergence of the complex power.
    """

    def __init__(self, status, sol):
        """
        Constructor.
        Init the exception.
        Save the solution.
        """

        # create the exception
        super().__init__("complex power has converged")

        # save the solution
        self.status = status
        self.sol = sol


class _IterCounter:
    """
    Simple class used as a callback to monitor the solver iterations.
    """

    def __init__(self, fct_conv, power_options):
        """
        Constructor.
        Init the counters.
        """

        # assign data
        self.fct_conv = fct_conv
        self.stop = power_options["stop"]
        self.n_min = power_options["n_min"]
        self.n_cmp = power_options["n_cmp"]
        self.rel_tol = power_options["rel_tol"]
        self.abs_tol = power_options["abs_tol"]

        # init data
        self.n_iter = 0
        self.power_vec = []
        self.power_final = None
        self.power_init = None
        self.sol = None

    def get_callback_run(self, sol):
        """
        Callback displaying and saving the iteration.
        Check the convergence on the complex power.
        If convergence is achieved, stop the solver and save the solution.
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

        # convergence iter condition
        n_iter_min = np.max([2, self.n_cmp + 1, self.n_min])

        # check for convergence
        if self.stop and (self.n_iter >= n_iter_min):
            # get best complex power
            power_ref = self.power_vec[-1]

            # get previous iteration
            power_cmp = self.power_vec[-(self.n_cmp + 1) : -1]

            # get convergence status
            power_err = np.max(np.abs(power_ref - power_cmp))
            power_thr = np.maximum(self.rel_tol * np.abs(power_ref), self.abs_tol)
            status = power_err <= power_thr

            # if convergence is achieved, stop the solver and save the solution
            if status:
                raise PowerConvergenceError(status, sol)

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

    def get_sol(self):
        """
        Get the temporary solution.
        """

        return self.sol

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

        op_count = sla.LinearOperator((n_dof, n_dof), matvec=fct, dtype=np.complex128)

        return op_count

    def get_fct_sys(self, op, n_dof):
        """
        Get a system operator that counts the number of evaluations.
        """

        def fct(x):
            self.n_sys_eval += 1
            y = op(x)
            return y

        op_count = sla.LinearOperator((n_dof, n_dof), matvec=fct, dtype=np.complex128)

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


def _fct_pcd_all(rhs_tmp, rhs, fct_pcd):
    """
    Function describing the preconditioner for the coupling system.
    """

    # extract
    (rhs_c, rhs_m) = rhs
    (fct_pcd_c, fct_pcd_m) = fct_pcd

    # get problem size
    n_dof_c = len(rhs_c)
    n_dof_m = len(rhs_m)

    # split vector
    rhs_c = rhs_tmp[0:n_dof_c]
    rhs_m = rhs_tmp[n_dof_c : n_dof_c + n_dof_m]

    # solve the preconditioner
    sol_c = fct_pcd_c(rhs_c)
    sol_m = fct_pcd_m(rhs_m)

    # assemble solution
    sol_all = np.concatenate((sol_c, sol_m))

    return sol_all


def _fct_sys_all(sol_tmp, rhs, fct_cpl, fct_sys):
    """
    Function describing the equation system for the coupling system.
    """

    # extract
    (rhs_c, rhs_m) = rhs
    (fct_cpl_c, fct_cpl_m) = fct_cpl
    (fct_sys_c, fct_sys_m) = fct_sys

    # get problem size
    n_dof_c = len(rhs_c)
    n_dof_m = len(rhs_m)

    # split vector
    sol_c = sol_tmp[0:n_dof_c]
    sol_m = sol_tmp[n_dof_c : n_dof_c + n_dof_m]

    # solve the system
    rhs_c = fct_sys_c(sol_c) + fct_cpl_c(sol_m)
    rhs_m = fct_sys_m(sol_m) + fct_cpl_m(sol_c)

    # assemble solution
    rhs_all = np.concatenate((rhs_c, rhs_m))

    return rhs_all


def _get_solver_direct(sol_init, fct_cpl, fct_sys, fct_pcd, rhs, direct_options, op_obj, iter_obj):
    """
    Solve the coupled magnetic-electric equation system with an iterative solver.
    """

    # extract
    (rhs_c, rhs_m) = rhs

    # get problem size
    n_dof_c = len(rhs_c)
    n_dof_m = len(rhs_m)

    # function describing the preconditioner
    def fct_pcd_all(rhs_tmp):
        return _fct_pcd_all(rhs_tmp, rhs, fct_pcd)

    # function describing the equation system
    def fct_sys_all(sol_tmp):
        return _fct_sys_all(sol_tmp, rhs, fct_cpl, fct_sys)

    # get operator
    op_pcd = op_obj.get_fct_pcd(fct_pcd_all, n_dof_c + n_dof_m)
    op_sys = op_obj.get_fct_sys(fct_sys_all, n_dof_c + n_dof_m)

    # get callback
    def fct_callback(sol):
        iter_obj.get_callback_run(sol)

    # assemble rhs
    rhs_all = np.concatenate((rhs_c, rhs_m))

    # call the solver
    (status, sol_all) = matrix_iterative.get_solve(sol_init, op_sys, op_pcd, rhs_all, fct_callback, direct_options)

    return status, sol_all


def _get_solver_domain(sol_init, sol_other, fct_cpl, fct_sys, fct_pcd, rhs, iter_options, op_obj):
    """
    Solve the electric or magnetic equation system with an iterative solver.
    """

    # get problem size
    n_dof = len(rhs)

    # function describing the preconditioner
    def fct_pcd_dom(rhs_tmp):
        return fct_pcd(rhs_tmp)

    # function describing the equation system
    def fct_sys_dom(sol_tmp):
        return fct_sys(sol_tmp)

    # get operator
    op_pcd = op_obj.get_fct_pcd(fct_pcd_dom, n_dof)
    op_sys = op_obj.get_fct_sys(fct_sys_dom, n_dof)

    # add coupling
    rhs_cpl = rhs - fct_cpl(sol_other)

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
    sol_m = sol_init[n_dof_c : n_dof_c + n_dof_m]

    # init
    converged = False
    status = None
    sol_all = None

    # solve
    while not converged:
        # solve and relax the electric equation systems
        (status_c, sol_c_new) = _get_solver_domain(sol_c, sol_m, fct_cpl_c, fct_sys_c, fct_pcd_c, rhs_c, iter_electric_options, op_obj)
        sol_c = (1 - relax_electric) * sol_c + relax_electric * sol_c_new

        # solve and relax the magnetic equation systems
        (status_m, sol_m_new) = _get_solver_domain(sol_m, sol_c, fct_cpl_m, fct_sys_m, fct_pcd_m, rhs_m, iter_magnetic_options, op_obj)
        sol_m = (1 - relax_magnetic) * sol_m + relax_magnetic * sol_m_new

        # get residuum
        res_c = fct_sys_c(sol_c) + fct_cpl_c(sol_m) - rhs_c
        res_m = fct_sys_m(sol_m) + fct_cpl_m(sol_c) - rhs_m

        # aggregate the results
        sol_all = np.concatenate((sol_c, sol_m))
        res_all = np.concatenate((res_c, res_m))
        rhs_all = np.concatenate((rhs_c, rhs_m))

        # run callback
        iter_obj.get_callback_run(sol_all)
        n_iter = iter_obj.get_n_iter()

        # check status
        res_thr = np.maximum(rel_tol * lna.norm(rhs_all), abs_tol)
        status_res = lna.norm(res_all) <= res_thr
        status = status_c and status_m and status_res

        # check convergence
        if (n_iter > n_max) or (status and (n_iter >= n_min)):
            converged = True

    return status, sol_all


def _get_status(status, sol_all, rhs, fct_cpl, fct_sys, status_options):
    """
    Compute the residuum and the solver convergence status.
    """

    # extract
    ignore_status = status_options["ignore_status"]
    ignore_res = status_options["ignore_res"]
    rel_tol = status_options["rel_tol"]
    abs_tol = status_options["abs_tol"]

    # extract
    (rhs_c, rhs_m) = rhs

    # get sol
    rhs_all = np.concatenate((rhs_c, rhs_m))
    out_all = _fct_sys_all(sol_all, rhs, fct_cpl, fct_sys)
    res_all = out_all - rhs_all

    # residuum threshold
    res_val = lna.norm(res_all)
    res_thr = np.maximum(rel_tol * lna.norm(rhs_all), abs_tol)

    # consider the solver status
    if ignore_status:
        status_solver = True
    else:
        status_solver = status

    # consider the residuum status
    if ignore_res:
        status_res = True
    else:
        status_res = res_val < res_thr

    # global status
    status = bool(status_res and status_solver)

    return status, res_all, res_val, res_thr


def get_solver(sol_init, fct_cpl, fct_sys, fct_pcd, rhs, fct_conv, solver_options):
    """
    Solve the equation system with an iterative solver.
    The equation system and the preconditioner are described with linear operator.
    """

    # get the condition options
    coupling = solver_options["coupling"]
    status_options = solver_options["status_options"]
    power_options = solver_options["power_options"]
    segregated_options = solver_options["segregated_options"]
    direct_options = solver_options["direct_options"]

    # get system size
    (rhs_c, rhs_m) = rhs
    n_dof_electric = len(rhs_c)
    n_dof_magnetic = len(rhs_m)
    n_dof_total = n_dof_electric + n_dof_magnetic

    # get initial solution
    if sol_init is None:
        sol_init = np.zeros(n_dof_total, dtype=np.complex128)

    # create operator and iter counter object
    op_obj = _OpCounter()
    iter_obj = _IterCounter(fct_conv, power_options)

    # call the solver
    LOGGER.debug("solver run")
    with LOGGER.BlockIndent():
        # first callback with the solution
        iter_obj.get_callback_init(sol_init)

        # start the solver
        LOGGER.debug("solver: start")

        # solve the equation system
        try:
            # run the solver
            if coupling == "direct":
                (status, sol) = _get_solver_direct(
                    sol_init,
                    fct_cpl,
                    fct_sys,
                    fct_pcd,
                    rhs,
                    direct_options,
                    op_obj,
                    iter_obj,
                )
            elif coupling == "segregated":
                (status, sol) = _get_solver_segregated(
                    sol_init,
                    fct_cpl,
                    fct_sys,
                    fct_pcd,
                    rhs,
                    segregated_options,
                    op_obj,
                    iter_obj,
                )
            else:
                raise ValueError("invalid coupling method")

            # residuum solver convergence
            LOGGER.debug("solver: residuum convergence")
        except PowerConvergenceError as ex:
            # power solver convergence
            LOGGER.debug("solver: power convergence")

            # get the solution
            status = ex.status
            sol = ex.sol

        # final callback with the solution
        iter_obj.get_callback_final(sol)

    # get convergence status
    (status, res, res_val, res_thr) = _get_status(status, sol, rhs, fct_cpl, fct_sys, status_options)

    # extract alg results
    n_sys_eval = op_obj.get_n_sys_eval()
    n_pcd_eval = op_obj.get_n_pcd_eval()
    n_iter = iter_obj.get_n_iter()
    conv = iter_obj.get_conv()

    # assign the results
    solver_status = {
        "n_dof_electric": n_dof_electric,
        "n_dof_magnetic": n_dof_magnetic,
        "n_dof_total": n_dof_total,
        "n_iter": n_iter,
        "n_sys_eval": n_sys_eval,
        "n_pcd_eval": n_pcd_eval,
        "res_val": res_val,
        "res_thr": res_thr,
        "status": status,
    }

    # display results
    LOGGER.debug("solver summary")
    with LOGGER.BlockIndent():
        # display results
        LOGGER.debug("status = %s" % status)
        LOGGER.debug("n_dof_total = %d" % n_dof_total)
        LOGGER.debug("n_dof_electric = %d" % n_dof_electric)
        LOGGER.debug("n_dof_magnetic = %d" % n_dof_magnetic)
        LOGGER.debug("n_iter = %d" % n_iter)
        LOGGER.debug("n_sys_eval = %d" % n_sys_eval)
        LOGGER.debug("n_pcd_eval = %d" % n_pcd_eval)
        LOGGER.debug("res_val = %.2e" % res_val)
        LOGGER.debug("res_thr = %.2e" % res_thr)

        # display status
        if status:
            LOGGER.debug("convergence achieved")
        else:
            LOGGER.warning("convergence issues")

    return sol, res, conv, status, solver_status


def get_condition(S_mat, conditions_options):
    """
    Compute an estimate of the condition number (norm 1) of preconditioner Schur complements.
    The condition number is used to detect problematic (quasi-singular) systems.
    """

    # get the condition options
    check = conditions_options["check"]
    tolerance_electric = conditions_options["tolerance_electric"]
    tolerance_magnetic = conditions_options["tolerance_magnetic"]
    norm_options = conditions_options["norm_options"]

    # extract matrices
    (S_mat_c, S_mat_m) = S_mat

    # check the condition
    if check:
        cond_electric = matrix_condition.get_condition_matrix("electric", S_mat_c, norm_options)
        cond_magnetic = matrix_condition.get_condition_matrix("magnetic", S_mat_m, norm_options)
        status = (cond_electric < tolerance_electric) and (cond_magnetic < tolerance_magnetic)
    else:
        cond_electric = float("nan")
        cond_magnetic = float("nan")
        status = True

    # cast to base type
    status = bool(status)

    # assign the results
    condition_status = {
        "check": check,
        "cond_electric": cond_electric,
        "cond_magnetic": cond_magnetic,
        "status": status,
    }

    # display status
    LOGGER.debug("condition summary")
    with LOGGER.BlockIndent():
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
