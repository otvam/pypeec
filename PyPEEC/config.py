# logging information
LOGGING_LEVEL = "INFO"
LOGGING_GLOBAL_TIMER = True

# matrix factorization options
MATRIX_FACTORIZATION = "UMFPACK"  # "SuperLU" or "UMFPACK"

# FFT options
FFT_SOLVER = "SciPy"  # "NumPy" or "SciPy" or "FFTW"
FFT_THREAD = 4  # used for FFTW (1 for no multi-threading)
FFT_BYTE = 16  # used for FFTW (None for automatic)
