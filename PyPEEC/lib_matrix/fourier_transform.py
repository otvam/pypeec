"""
This module is used as a common interface for different FFT libraries:
    - NumPy FFT library
    - SciPy FFT library
    - FFTW FFT library (available through pyFFTW)

WARNING: Not all versions of FFTW are compiled with multithreading support.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import os
from PyPEEC.lib_utils import config

# get config
SOLVER = config.FFT_OPTIONS["SOLVER"]
FFTS_WORKER = config.FFT_OPTIONS["FFTS_WORKER"]
FFTW_THREAD = config.FFT_OPTIONS["FFTW_THREAD"]
FFTW_CACHE_TIMEOUT = config.FFT_OPTIONS["FFTW_CACHE_TIMEOUT"]
FFTW_BYTE_ALIGN = config.FFT_OPTIONS["FFTW_BYTE_ALIGN"]

# import the right library
if SOLVER == "SciPy":
    # import the SciPy FFT module
    import scipy.fft as ffts

    # set the number of workers
    if FFTS_WORKER is None:
        FFTS_WORKER = os.cpu_count()
elif SOLVER == "FFTW":
    # import the FFTW binding
    import pyfftw
    import pyfftw.interfaces.cache as cache
    import pyfftw.interfaces.numpy_fft as fftw

    # set the number of threads
    if FFTW_THREAD is None:
        FFTW_THREAD = os.cpu_count()

    # configure the FFT cache
    if FFTW_CACHE_TIMEOUT is None:
        cache.disable()
    else:
        cache.enable()
        cache.set_keepalive_time(FFTW_CACHE_TIMEOUT)
else:
    raise ValueError("invalid FFT library")


def _get_fftn(mat, shape, axes):
    """
    Get the N-D FFT of a tensor along the specified axes.
    The size of the output tensor is specified.
    """

    if SOLVER == "SciPy":
        mat_trf = ffts.fftn(mat, shape, axes=axes, workers=FFTS_WORKER)
    elif SOLVER == "FFTW":
        mat = pyfftw.byte_align(mat, n=FFTW_BYTE_ALIGN)
        mat_trf = fftw.fftn(mat, shape, axes=axes, threads=FFTW_THREAD)
    else:
        raise ValueError("invalid FFT library")

    return mat_trf


def _get_ifftn(mat, shape, axes):
    """
    Get the N-D iFFT of a tensor along the specified axes.
    The size of the output tensor is specified.
    """

    if SOLVER == "SciPy":
        mat_trf = ffts.ifftn(mat, shape, axes=axes, workers=FFTS_WORKER)
    elif SOLVER == "FFTW":
        mat = pyfftw.byte_align(mat, n=FFTW_BYTE_ALIGN)
        mat_trf = fftw.ifftn(mat, shape, axes=axes, threads=FFTW_THREAD)
    else:
        raise ValueError("invalid FFT library")

    return mat_trf


def _get_fct_tensor(mat, double_dim, fct):
    """
    Get the FFT/iFFT of a 4D tensor along the first 3D.
    The size of the output is:
        - the same of the input
        - the double of the input
    """

    # get the tensor size
    (nx, ny, nz, nd) = mat.shape

    # double the dimension if required
    if double_dim:
        nx = 2*nx
        ny = 2*ny
        nz = 2*nz

    mat_trf = fct(mat, (nx, ny, nz), (0, 1, 2))

    return mat_trf


def get_fft_tensor(mat, double_dim):
    """
    Get the FFT of a 4D tensor along the first 3D.
    The size of the output is:
        - the same of the input
        - the double of the input
    """

    return _get_fct_tensor(mat, double_dim, _get_fftn)


def get_ifft_tensor(mat, double_dim):
    """
    Get the iFFT of a 4D tensor along the first 3D.
    The size of the output is:
        - the same of the input
        - the double of the input
    """

    return _get_fct_tensor(mat, double_dim, _get_ifftn)
