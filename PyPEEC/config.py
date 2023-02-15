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
LOGGING_LEVEL = "INFO"  # logging level for the handlers
LOGGING_GLOBAL_TIMER = True  # use a global timer (or not) for the different handlers
LOGGING_INDENTATION = 4  # indentation level for the blocks

# matrix factorization options
#   - SuperLU is typically slower but integrated with SciPy
#   - UMFPACK is typically faster but has to be installed separately
MATRIX_FACTORIZATION = "SuperLU"  # "SuperLU" or "UMFPACK"

# method for dense matrix multiplication
#   - FFT for doing the multiplication with circulant tensors and FFT
#   - DIRECT for standard matrix multiplication (extremely slow and memory intensive)
MATRIX_MULTIPLICATION = "FFT"  # "FFT" or "DIRECT"

# FFT options
#   - NumPy is not very fast
#   - SciPy is typically faster than NumPy
#   - FFTW is typically faster but has to be installed separately
FFT_SOLVER = "SciPy"  # "NumPy" or "SciPy" or "FFTW"

# FFT handling
#   - if true, then the FFT is done separately for each dimension
#   - if false, then the FFT is done at once for the complete tensor
FFT_SPLIT_TENSOR = False  # split (or not) the tensors for the FFT

# FFT library options
FFTS_WORKER = None  # number of workers for SciPy (None for default)
FFTW_THREAD = 4  # used for FFTW (number of threads, 1 for no multi-threading)
FFTW_CACHE_TIMEOUT = 100  # used for FFTW (cache timeout in seconds)
FFTW_BYTE_ALIGN = 16  # used for FFTW (size for byte alignment)
