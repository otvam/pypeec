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
from pypeec.lib_utils import config

# get FFT config
FFT_LIBRARY = config.FFT_LIBRARY
FFT_OPTIONS = config.FFT_OPTIONS

# import the right library
if FFT_LIBRARY == "CuPy":
    import cupy.fft as fftc
elif FFT_LIBRARY == "SciPy":
    import scipy.fft as ffts
elif FFT_LIBRARY == "FFTW":
    # import the FFTW binding
    import pyfftw
    import pyfftw.interfaces.cache as cache
    import pyfftw.interfaces.numpy_fft as fftw

    # configure the FFT cache
    if FFT_OPTIONS.FFTW_CACHE_TIMEOUT is None:
        cache.disable()
    else:
        cache.enable()
        cache.set_keepalive_time(FFT_OPTIONS.FFTW_CACHE_TIMEOUT)
else:
    raise ValueError("invalid FFT library")


def _get_fftn(mat, shape, axes):
    """
    Get the N-D FFT of a tensor along the specified axes.
    The size of the output tensor is specified.
    """

    if FFT_LIBRARY == "CuPy":
        mat_trf = fftc.fftn(mat, shape, axes=axes)
    elif FFT_LIBRARY == "SciPy":
        mat_trf = ffts.fftn(mat, shape, axes=axes, workers=FFT_OPTIONS.FFTS_WORKER)
    elif FFT_LIBRARY == "FFTW":
        mat = pyfftw.byte_align(mat, n=FFT_OPTIONS.FFTW_BYTE_ALIGN)
        mat_trf = fftw.fftn(mat, shape, axes=axes, threads=FFT_OPTIONS.FFTW_THREAD)
    else:
        raise ValueError("invalid FFT library")

    return mat_trf


def _get_ifftn(mat, shape, axes):
    """
    Get the N-D iFFT of a tensor along the specified axes.
    The size of the output tensor is specified.
    """

    if FFT_LIBRARY == "CuPy":
        mat_trf = fftc.ifftn(mat, shape, axes=axes)
    elif FFT_LIBRARY == "SciPy":
        mat_trf = ffts.ifftn(mat, shape, axes=axes, workers=FFT_OPTIONS.FFTS_WORKER)
    elif FFT_LIBRARY == "FFTW":
        mat = pyfftw.byte_align(mat, n=FFT_OPTIONS.FFTW_BYTE_ALIGN)
        mat_trf = fftw.ifftn(mat, shape, axes=axes, threads=FFT_OPTIONS.FFTW_THREAD)
    else:
        raise ValueError("invalid FFT library")

    return mat_trf


def get_fft_tensor_keep(mat):
    """
    Get the FFT of a 4D tensor along the first 3D.
    The size of the output is the same of the input
    """

    return _get_fftn(mat, None, (0, 1, 2))


def get_fft_tensor_expand(mat):
    """
    Get the FFT of a 4D tensor along the first 3D.
    The size of the output is the double the size of the input
    """

    # get the tensor size
    (nx, ny, nz, nd) = mat.shape

    return _get_fftn(mat, (2*nx, 2*ny, 2*nz), (0, 1, 2))


def get_ifft_tensor(mat):
    """
    Get the iFFT of a 4D tensor along the first 3D.
    The size of the output is the same of the input
    """

    return _get_ifftn(mat, None, (0, 1, 2))
