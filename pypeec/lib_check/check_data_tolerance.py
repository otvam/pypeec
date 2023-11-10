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


def _check_solver_options(solver_options):
    """
    Check the matrix solver options.
    """

    # check type
    key_list = ["check", "tolerance", "iter_options"]
    datachecker.check_dict("solver_options", solver_options, key_list=key_list)

    # extract field
    check = solver_options["check"]
    tolerance = solver_options["tolerance"]
    iter_options = solver_options["iter_options"]

    # check the data
    datachecker.check_boolean("tolerance", check)
    datachecker.check_float("tolerance", tolerance, is_positive=True, can_be_zero=False)

    # check the data
    key_list = ["solver", "rel_tol", "abs_tol", "n_inner", "n_outer"]
    datachecker.check_dict("iter_options", iter_options, key_list=key_list)
    datachecker.check_choice("solver", iter_options["solver"], ["gmres", "gcrot"])
    datachecker.check_float("rel_tol", iter_options["rel_tol"], is_positive=True, can_be_zero=False)
    datachecker.check_float("abs_tol", iter_options["abs_tol"], is_positive=True, can_be_zero=False)
    datachecker.check_integer("n_inner", iter_options["n_inner"], is_positive=True, can_be_zero=False)
    datachecker.check_integer("n_outer", iter_options["n_outer"], is_positive=True, can_be_zero=False)


def _check_condition_options(condition_options):
    """
    Check the matrix condition number check options.
    """

    # check type
    key_list = ["check", "tolerance", "norm_options"]
    datachecker.check_dict("condition_options", condition_options, key_list=key_list)

    # extract field
    check = condition_options["check"]
    tolerance = condition_options["tolerance"]
    norm_options = condition_options["norm_options"]

    # check the data
    datachecker.check_boolean("tolerance", check)
    datachecker.check_float("tolerance", tolerance, is_positive=True, can_be_zero=False)

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

    # check data
    datachecker.check_choice("mult_type", mult_type, ["fft", "direct"])
    datachecker.check_float("green_simplify", green_simplify, is_positive=True, can_be_zero=False)
    datachecker.check_float("coupling_simplify", coupling_simplify, is_positive=True, can_be_zero=False)

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
