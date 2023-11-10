"""
Module for computer FFT/iFFT of tensors.

This module is used as a common interface for different FFT libraries:
    - SciPy FFT library
    - FFTW FFT library (available through pyFFTW)
    - CuPy FFT library (computation with GPUs)
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import os

# dummy functions
FFTN = None
IFFTN = None


def set_options(fft_options):
    """
    Assign the options and load the right libray.
    """

    # assign global variable
    library = fft_options["library"]
    scipy_worker = fft_options["scipy_worker"]
    fftw_thread = fft_options["fftw_thread"]
    fftw_timeout = fft_options["fftw_timeout"]
    fftw_byte_align = fft_options["fftw_byte_align"]

    # import the right library
    if library == "CuPy":
        import cupy.fft as fftc

        # find FFTN function
        def fct_fftn(mat, shape, axes, _):
            return fftc.fftn(mat, shape, axes=axes)

        # find iFFTN function
        def fct_ifftn(mat, shape, axes, _):
            return fftc.ifftn(mat, shape, axes=axes)
    elif library == "SciPy":
        import scipy.fft as ffts

        # find the number of workers
        if scipy_worker is None:
            scipy_worker = os.cpu_count()

        # find FFTN function
        def fct_fftn(mat, shape, axes, replace):
            return ffts.fftn(mat, shape, axes=axes, overwrite_x=replace, workers=scipy_worker)

        # find iFFTN function
        def fct_ifftn(mat, shape, axes, replace):
            return ffts.ifftn(mat, shape, axes=axes, overwrite_x=replace, workers=scipy_worker)
    elif library == "FFTW":
        import pyfftw
        from pyfftw.interfaces import cache
        from pyfftw.interfaces import numpy_fft

        # get options
        fftw_thread = fft_options["fftw_thread"]
        fftw_timeout = fft_options["fftw_timeout"]
        fftw_byte_align = fft_options["fftw_byte_align"]

        # find the number of threads
        if fftw_thread is None:
            fftw_thread = os.cpu_count()

        # configure the FFT cache
        if fftw_timeout is None:
            cache.disable()
        else:
            cache.enable()
            cache.set_keepalive_time(fftw_timeout)

        # find FFTN function
        def fct_fftn(mat, shape, axes, replace):
            mat = pyfftw.byte_align(mat, n=fftw_byte_align)
            return numpy_fft.fftn(mat, shape, axes=axes, overwrite_input=replace, threads=fftw_thread)

        # find iFFTN function
        def fct_ifftn(mat, shape, axes, replace):
            mat = pyfftw.byte_align(mat, n=fftw_byte_align)
            return numpy_fft.ifftn(mat, shape, axes=axes, overwrite_input=replace, threads=fftw_thread)
    else:
        raise ValueError("invalid FFT library")

    # assign transforms functions
    global FFTN
    global IFFTN
    FFTN = fct_fftn
    IFFTN = fct_ifftn


def get_fft_tensor_keep(mat, replace):
    """
    Get the FFT of a 4D tensor along the first 3D.
    The size of the output is the same of the input
    """

    mat_trf = FFTN(mat, None, (0, 1, 2), replace)

    return mat_trf


def get_fft_tensor_expand(mat, replace):
    """
    Get the FFT of a 4D tensor along the first 3D.
    The size of the output is the double the size of the input
    """

    # get the tensor size
    (nx, ny, nz) = mat.shape[0:3]

    # get the transform
    mat_trf = FFTN(mat, (2*nx, 2*ny, 2*nz), (0, 1, 2), replace)

    return mat_trf


def get_ifft_tensor(mat, replace):
    """
    Get the iFFT of a 4D tensor along the first 3D.
    The size of the output is the same of the input
    """

    mat_trf = IFFTN(mat, None, (0, 1, 2), replace)

    return mat_trf
