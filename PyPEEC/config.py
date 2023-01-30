"""
Configuration of the program.
Defined with global variables.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import os

# get the path of the root of the code
PATH_ROOT = os.path.dirname(__file__)

# logging information
LOGGING_LEVEL = "INFO"
LOGGING_GLOBAL_TIMER = True

# matrix factorization options
MATRIX_FACTORIZATION = "SuperLU"  # "SuperLU" or "UMFPACK"

# method for dense matrix multiplication
MATRIX_MULTIPLICATION = "DIRECT"  # "FFT" or "DIRECT"

# FFT options
FFT_SOLVER = "SciPy"  # "NumPy" or "SciPy" or "FFTW"
FFT_SPLIT_TENSOR = False  # split (or not) the tensors for the FFT
FFTS_WORKER = None # number of workers for SciPy (None for default)
FFTW_THREAD = 4  # used for FFTW (number of threads, 1 for no multi-threading)
FFTW_CACHE_TIMEOUT = 100  # used for FFTW (cache timeout in seconds)
FFTW_BYTE_ALIGN = 16  # used for FFTW (size for byte alignment)
