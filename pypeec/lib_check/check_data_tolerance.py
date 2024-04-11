"""
Module for checking the solver tolerance data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

from pypeec.lib_check import datachecker


def _check_fft_options(fft_options):
    """
    Check the FFT algorithm options.
    """

    # check type
    key_list = [
        "matrix_split",
        "library",
        "scipy_worker",
        "fftw_thread",
        "fftw_timeout",
        "fftw_byte_align",
    ]
    datachecker.check_dict("fft_options", fft_options, key_list=key_list)

    # extract field
    matrix_split = fft_options["matrix_split"]
    library = fft_options["library"]
    scipy_worker = fft_options["scipy_worker"]
    fftw_thread = fft_options["fftw_thread"]
    fftw_timeout = fft_options["fftw_timeout"]
    fftw_byte_align = fft_options["fftw_byte_align"]

    # check the data
    datachecker.check_boolean("matrix_split", matrix_split)
    datachecker.check_choice("library", library, ["SciPy", "FFTW", "CuPy"])
    datachecker.check_integer("scipy_worker", scipy_worker, is_positive=True, can_be_zero=False, can_be_none=True)
    datachecker.check_integer("fftw_thread", fftw_thread, is_positive=True, can_be_zero=False, can_be_none=True)
    datachecker.check_integer("fftw_byte_align", fftw_byte_align, is_positive=True, can_be_zero=False, can_be_none=True)
    datachecker.check_float("fftw_timeout", fftw_timeout, is_positive=True, can_be_zero=True, can_be_none=True)


def _check_factorization_options(factorization_options):
    """
    Check the matrix factorization options.
    """

    # check type
    key_list = ["library", "pyamg_options", "pardiso_options"]
    datachecker.check_dict("factorization_options", factorization_options, key_list=key_list)

    # extract field
    library = factorization_options["library"]
    pyamg_options = factorization_options["pyamg_options"]
    pardiso_options = factorization_options["pardiso_options"]

    # check the data
    datachecker.check_choice("library", library, ["SuperLU", "UMFPACK", "PARDISO", "PyAMG"])

    # check the data
    key_list = ["tol", "solver", "krylov"]
    datachecker.check_dict("pyamg_options", pyamg_options, key_list=key_list)
    datachecker.check_choice("solver", pyamg_options["solver"], ["adapt", "root"])
    datachecker.check_choice("krylov", pyamg_options["krylov"], ["gmres", "fgmres"], can_be_none=True)
    datachecker.check_float("tol", pyamg_options["tol"], is_positive=True, can_be_zero=False)

    # check the data
    key_list = ["thread_pardiso", "thread_mkl"]
    datachecker.check_dict("pardiso_options", pardiso_options, key_list=key_list)
    datachecker.check_integer("thread_pardiso", pardiso_options["thread_pardiso"], is_positive=True, can_be_zero=False, can_be_none=True)
    datachecker.check_integer("thread_mkl",  pardiso_options["thread_mkl"], is_positive=True, can_be_zero=False, can_be_none=True)


def _check_iter_options(iter_options):
    """
    Check the iterative solver options.
    """

    # check type
    key_list = ["solver", "rel_tol", "abs_tol", "n_inner", "n_outer"]
    datachecker.check_dict("iter_options", iter_options, key_list=key_list)

    # check data
    datachecker.check_choice("solver", iter_options["solver"], ["gmres", "gcrot"])
    datachecker.check_float("rel_tol", iter_options["rel_tol"], is_positive=True, can_be_zero=False)
    datachecker.check_float("abs_tol", iter_options["abs_tol"], is_positive=True, can_be_zero=False)
    datachecker.check_integer("n_inner", iter_options["n_inner"], is_positive=True, can_be_zero=False)
    datachecker.check_integer("n_outer", iter_options["n_outer"], is_positive=True, can_be_zero=False)


def _check_solver_options(solver_options):
    """
    Check the equation system solver options.
    """

    # check type
    key_list = ["coupling", "power_options", "tolerance_options", "segregated_options", "direct_options"]
    datachecker.check_dict("solver_options", solver_options, key_list=key_list)

    # extract field
    coupling = solver_options["coupling"]
    power_options = solver_options["power_options"]
    tolerance_options = solver_options["tolerance_options"]
    segregated_options = solver_options["segregated_options"]
    direct_options = solver_options["direct_options"]

    # check the coupling
    datachecker.check_choice("coupling", coupling, ["direct", "segregated"])

    # check the power options
    key_list = ["stop", "n_min", "n_cmp", "rel_tol", "abs_tol"]
    datachecker.check_dict("power_options", power_options, key_list=key_list)
    datachecker.check_integer("n_min", power_options["n_min"], is_positive=True, can_be_zero=False)
    datachecker.check_integer("n_cmp", power_options["n_cmp"], is_positive=True, can_be_zero=False)
    datachecker.check_float("rel_tol", power_options["rel_tol"], is_positive=True, can_be_zero=False)
    datachecker.check_float("abs_tol", power_options["abs_tol"], is_positive=True, can_be_zero=False)
    datachecker.check_boolean("stop", power_options["stop"])

    # check the tolerance options
    key_list = ["ignore_status", "ignore_res", "rel_tol", "abs_tol"]
    datachecker.check_dict("tolerance_options", tolerance_options, key_list=key_list)
    datachecker.check_float("rel_tol", tolerance_options["rel_tol"], is_positive=True, can_be_zero=False)
    datachecker.check_float("abs_tol", tolerance_options["abs_tol"], is_positive=True, can_be_zero=False)
    datachecker.check_boolean("ignore_status", tolerance_options["ignore_status"])
    datachecker.check_boolean("ignore_res", tolerance_options["ignore_res"])

    # check the direct solver
    _check_iter_options(direct_options)

    # check the segregated solver
    key_list = [
        "rel_tol", "abs_tol",
        "n_min", "n_max",
        "relax_electric", "relax_magnetic",
        "iter_electric_options", "iter_magnetic_options",
    ]
    datachecker.check_dict("segregated_options", segregated_options, key_list=key_list)
    datachecker.check_float("rel_tol", segregated_options["rel_tol"], is_positive=True, can_be_zero=False)
    datachecker.check_float("abs_tol", segregated_options["abs_tol"], is_positive=True, can_be_zero=False)
    datachecker.check_integer("n_min", segregated_options["n_min"], is_positive=True, can_be_zero=False)
    datachecker.check_integer("n_max", segregated_options["n_max"], is_positive=True, can_be_zero=False)
    datachecker.check_float("relax_electric", segregated_options["relax_electric"], is_positive=True, can_be_zero=False)
    datachecker.check_float("relax_magnetic", segregated_options["relax_magnetic"], is_positive=True, can_be_zero=False)
    _check_iter_options(segregated_options["iter_electric_options"])
    _check_iter_options(segregated_options["iter_magnetic_options"])


def _check_condition_options(condition_options):
    """
    Check the matrix condition number check options.
    """

    # check type
    key_list = ["check", "tolerance_electric", "tolerance_magnetic", "norm_options"]
    datachecker.check_dict("condition_options", condition_options, key_list=key_list)

    # extract field
    check = condition_options["check"]
    tolerance_electric = condition_options["tolerance_electric"]
    tolerance_magnetic = condition_options["tolerance_magnetic"]
    norm_options = condition_options["norm_options"]

    # check the data
    datachecker.check_boolean("check", check)
    datachecker.check_float("tolerance_electric", tolerance_electric, is_positive=True, can_be_zero=False)
    datachecker.check_float("tolerance_magnetic", tolerance_magnetic, is_positive=True, can_be_zero=False)

    # check the data
    key_list = ["t_accuracy", "n_iter_max"]
    datachecker.check_dict("norm_options", norm_options, key_list=key_list)
    datachecker.check_integer("t_accuracy", norm_options["t_accuracy"], is_positive=True, can_be_zero=False)
    datachecker.check_integer("n_iter_max", norm_options["n_iter_max"], is_positive=True, can_be_zero=False)


def check_data_tolerance(data_tolerance):
    """
    Check the solver tolerance data:
        - Green functions simplification
        - Coupling functions simplification
        - matrix multiplication algorithm
        - FFT algorithm options
        - matrix factorization options
        - iterative solver options
        - matrix condition options
    """

    # check type
    key_list = [
        "sweep_pool",
        "green_simplify",
        "coupling_simplify",
        "mult_type",
        "factorization_options",
        "fft_options",
        "solver_options",
        "condition_options",
    ]
    datachecker.check_dict("data_tolerance", data_tolerance, key_list=key_list)

    # extract field
    mult_type = data_tolerance["mult_type"]
    green_simplify = data_tolerance["green_simplify"]
    coupling_simplify = data_tolerance["coupling_simplify"]
    sweep_pool = data_tolerance["sweep_pool"]

    # check data
    datachecker.check_choice("mult_type", mult_type, ["fft", "direct"])
    datachecker.check_float("green_simplify", green_simplify, is_positive=True, can_be_zero=False)
    datachecker.check_float("coupling_simplify", coupling_simplify, is_positive=True, can_be_zero=False)
    datachecker.check_integer("sweep_pool", sweep_pool, is_positive=True, can_be_zero=False, can_be_none=True)

    # extract field
    fft_options = data_tolerance["fft_options"]
    factorization_options = data_tolerance["factorization_options"]
    solver_options = data_tolerance["solver_options"]
    condition_options = data_tolerance["condition_options"]

    # check solver and condition check options
    _check_fft_options(fft_options)
    _check_factorization_options(factorization_options)
    _check_solver_options(solver_options)
    _check_condition_options(condition_options)
