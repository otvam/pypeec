"""
Module for doing matrix-vector multiplication with the circulant tensors and FFT.

This module is used as a common interface for different FFT libraries:
    - NumPy FFT library
    - SciPy FFT library
    - FFTW FFT library (available with pyFFTW)

WARNING: Not all versions of FFTW are compiled with multithreading support.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np
from PyPEEC import config

# get config
FFT_SOLVER = config.FFT_SOLVER
FFT_THREAD = config.FFT_THREAD
FFT_CACHE_TIMEOUT = config.FFT_CACHE_TIMEOUT
FFT_BYTE_ALIGN = config.FFT_BYTE_ALIGN
FFT_SPLIT_TENSOR = config.FFT_SPLIT_TENSOR

# import the right library
if FFT_SOLVER == "NumPy":
    import numpy.fft as fftn
elif FFT_SOLVER == "SciPy":
    import scipy.fft as ffts
elif FFT_SOLVER == "FFTW":
    import pyfftw
    import pyfftw.interfaces.numpy_fft as fftw
    import pyfftw.interfaces.cache as cache

    # the cache for the FFT dimension should be enabled
    cache.enable()

    # the cache has a timeout
    cache.set_keepalive_time(FFT_CACHE_TIMEOUT)
else:
    raise ValueError("invalid FFT library")


def _get_fftn(mat, shape, axes):
    """
    Get the N-D FFT of a tensor along the specified axes.
    The size of the output tensor is specified.
    """

    if FFT_SOLVER == "NumPy":
        mat_trf = fftn.fftn(mat, shape, axes=axes)
    elif FFT_SOLVER == "SciPy":
        mat_trf = ffts.fftn(mat, shape, axes=axes)
    elif FFT_SOLVER == "FFTW":
        mat = pyfftw.byte_align(mat, n=FFT_BYTE_ALIGN)
        mat_trf = fftw.fftn(mat, shape, axes=axes, threads=FFT_THREAD)
    else:
        raise ValueError("invalid FFT library")

    return mat_trf


def _get_ifftn(mat, shape, axes):
    """
    Get the N-D iFFT of a tensor along the specified axes.
    The size of the output tensor is specified.
    """

    if FFT_SOLVER == "NumPy":
        mat_trf = fftn.ifftn(mat, shape, axes=axes)
    elif FFT_SOLVER == "SciPy":
        mat_trf = ffts.ifftn(mat, shape, axes=axes)
    elif FFT_SOLVER == "FFTW":
        mat = pyfftw.byte_align(mat, n=FFT_BYTE_ALIGN)
        mat_trf = fftw.ifftn(mat, shape, axes=axes, threads=FFT_THREAD)
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

    # compute the tensor (with a loop or directly)
    if FFT_SPLIT_TENSOR:
        mat_trf = np.empty((nx, ny, nz, nd), dtype=np.complex128)
        for i in range(nd):
            mat_trf[:, :, :, i] = fct(mat[:, :, :, i], (nx, ny, nz), (0, 1, 2))
    else:
        mat_trf = fct(mat, (nx, ny, nz), (0, 1, 2))

    return mat_trf


def _get_fft_tensor(mat, double_dim):
    """
    Get the FFT of a 4D tensor along the first 3D.
    The size of the output is:
        - the same of the input
        - the double of the input
    """

    return _get_fct_tensor(mat, double_dim, _get_fftn)


def _get_ifft_tensor(mat, double_dim):
    """
    Get the iFFT of a 4D tensor along the first 3D.
    The size of the output is:
        - the same of the input
        - the double of the input
    """

    return _get_fct_tensor(mat, double_dim, _get_ifftn)


def get_circulant_tensor(mat):
    """
    Construct a circulant tensor from a 4D tensor.
    The circulant tensor is constructed for the first 3D.
    The size of the circulant tensor is twice the size of the original tensor.
    """

    # get the tensor size
    (nx, ny, nz, nd) = mat.shape

    # init the circulant tensor
    mat_circulant = np.zeros((2*nx, 2*ny, 2*nz, nd), dtype=np.float64)

    # cube xyz
    mat_circulant[0:nx, 0:ny, 0:nz, :] = mat[0:nx, 0:ny, 0:nz, :]
    # cube x
    mat_circulant[nx+1:2*nx, 0:ny, 0:nz, :] = mat[nx-1:0:-1, 0:ny, 0:nz, :]
    # cube y
    mat_circulant[0:nx, ny+1:2*ny, 0:nz, :] = mat[0:nx, ny-1:0:-1, 0:nz, :]
    # cube z
    mat_circulant[0:nx, 0:ny, nz+1:2*nz, :] = mat[0:nx, 0:ny, nz-1:0:-1, :]
    # cube xy
    mat_circulant[nx+1:2*nx, ny+1:2*ny, 0:nz, :] = mat[nx-1:0:-1, ny-1:0:-1, 0:nz, :]
    # cube xz
    mat_circulant[nx+1:2*nx, 0:ny, nz+1:2*nz, :] = mat[nx-1:0:-1, 0:ny, nz-1:0:-1, :]
    # cube yz
    mat_circulant[0:nx, ny+1:2*ny, nz+1:2*nz, :] = mat[0:nx, ny-1:0:-1, nz-1:0:-1, :]
    # cube xyz
    mat_circulant[nx+1:2*nx, ny+1:2*ny, nz+1:2*nz, :] = mat[nx-1:0:-1, ny-1:0:-1, nz-1:0:-1, :]

    # get the FFT of the circulant tensor
    mat_circulant_fft = _get_fft_tensor(mat_circulant, False)

    return mat_circulant_fft


def get_circulant_multiply(mat_circulant_fft, vec):
    """
    Matrix-vector multiplication with FFT.
    The matrix is shaped as a FFT circulant tensor.
    The vector is also shaped as a tensor.

    The size of the matrix (FFT circulant tensor) is twice the size of the vector (tensor).
    The size of the vector (tensor) is doubled during the FFT operation.
    The size of result is the same as the size of the vector.
    """

    # get the tensor size
    (nx, ny, nz, nd) = vec.shape

    # compute the FFT of the vector (result is the same size as the FFT circulant tensor)
    vec_fft = _get_fft_tensor(vec, True)

    # matrix vector multiplication in frequency domain with the FFT circulant tensor
    res_fft = mat_circulant_fft*vec_fft

    # compute the iFFT
    res = _get_ifft_tensor(res_fft, False)

    # the result is in the first block of the matrix
    res = res[0:nx, 0:ny, 0:nz, :]

    return res
