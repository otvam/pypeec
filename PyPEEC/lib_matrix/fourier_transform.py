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


def _get_prepare_vector(nx, ny, nz, nd, idx, vec):
    """
    Prepare a vector for the circulant FFT multiplication.
    """

    # expand the vector into a vector with all the dimention
    vec_all = np.zeros(nx*ny*nz*nd, dtype=np.complex128)
    vec_all[idx] = vec

    # reshape the vector into a tensor
    vec_all = vec_all.reshape((nx, ny, nz, nd), order="F")

    return vec_all


def _get_extract_vector(idx, vec_all):
    """
    Extract a vector from the circulant FFT multiplication result.
    """

    # flatten the tensor into a vector
    vec_all = vec_all.flatten(order="F")

    # select the elements
    vec = vec_all[idx]

    return vec


def get_circulant_tensor(mat):
    """
    Construct a circulant tensor from a 4D tensor.
    The circulant tensor is constructed for the first 3D.

    The input tensor has the size: (nx, ny, nz, nd).
    The output FFT circulant tensor has the size: (2*nx, 2*ny, 2*nz, nd).
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


def get_circulant_multiply(mat_circulant_fft, idx, vec):
    """
    Matrix-vector multiplication with FFT.
    The matrix is shaped as a FFT circulant tensor.

    The input vector has the size: n_i.
    The input FFT circulant tensor has the size: (2*nx, 2*ny, 2*nz, nd).
    The output vector has the size: n_i.

    For the matrix-vector multiplication is done in several steps:
        - the vector is expanded into a tensor: n_i to (nx, ny, nz, nd)
        - computation the FFT of the obtained tensor: (nx, ny, nz, nd) to (2*nx, 2*ny, 2*nz, nd)
        - multiplication of FFT circulant tensors: (2*nx, 2*ny, 2*nz, nd)
        - computation the iFFT of the obtained tensor: (2*nx, 2*ny, 2*nz, nd)
        - shrinking of the obtained tensor: (2*nx, 2*ny, 2*nz, nd) to (nx, ny, nz, nd)
        - the tensor is flattened into a vector: (nx, ny, nz, nd) to n_i
    """

    # get the tensor size
    (nx, ny, nz, nd) = mat_circulant_fft.shape
    nx = int(nx/2)
    ny = int(ny/2)
    nz = int(nz/2)

    # prepare the vector (transform the vector into a tensor)
    vec_all = _get_prepare_vector(nx, ny, nz, nd, idx, vec)

    # compute the FFT of the vector (result is the same size as the FFT circulant tensor)
    vec_all_fft = _get_fft_tensor(vec_all, True)

    # matrix vector multiplication in frequency domain with the FFT circulant tensor
    res_all_fft = mat_circulant_fft*vec_all_fft

    # compute the iFFT
    res_all = _get_ifft_tensor(res_all_fft, False)

    # the result is in the first block of the matrix
    res_all = res_all[0:nx, 0:ny, 0:nz, :]

    # extract the vector (transform the tensor into a vector)
    res = _get_extract_vector(idx, res_all)

    return res
