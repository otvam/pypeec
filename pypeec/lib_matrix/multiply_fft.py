"""
Module for doing matrix-vector multiplication (with circulant tensors and FFT).

Three different types of matrices are supported:
    - single: tensor representing a simple matrix (number of dimensions = 1)
    - diag: tensor representing a block diagonal matrix (number of dimensions = 3)
    - cross: tensor representing a block off-diagonal matrix (number of dimensions = 3)
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

from pypeec.lib_utils import config
from pypeec.lib_matrix import fourier_transform

# get GPU config
USE_GPU = config.USE_GPU

# load the GPU and CPU libraries
if USE_GPU:
    import cupy as cp
else:
    import numpy as cp


def _get_tensor_sign(matrix_type):
    """
    Get the signs for the different tensor blocks.
    """

    if matrix_type == "single":
        sign = cp.ones((2, 2, 2, 1), dtype=cp.int_)
    elif matrix_type == "diag":
        sign = cp.ones((2, 2, 2, 3), dtype=cp.int_)
    elif matrix_type == "cross":
        sign = cp.empty((2, 2, 2, 3), dtype=cp.int_)
        sign[0, 0, 0, :] = [+1, +1, +1]
        sign[1, 0, 0, :] = [-1, +1, +1]
        sign[0, 1, 0, :] = [+1, -1, +1]
        sign[0, 0, 1, :] = [+1, +1, -1]
        sign[1, 1, 0, :] = [-1, -1, +1]
        sign[1, 0, 1, :] = [-1, +1, -1]
        sign[0, 1, 1, :] = [+1, -1, -1]
        sign[1, 1, 1, :] = [-1, -1, -1]
    else:
        raise ValueError("invalid matrix type")

    return sign


def _get_tensor_circulant(mat, sign):
    """
    Construct a circulant tensor from a 4D tensor.
    The circulant tensor is constructed for the first 3D.

    The input tensor has the size: (nx, ny, nz, nd).
    The output FFT circulant tensor has the size: (2*nx, 2*ny, 2*nz, nd).
    """

    # load the data to the GPU
    if USE_GPU:
        mat = cp.asarray(mat)

    # get the tensor size
    (nx, ny, nz, nd) = mat.shape

    # init the circulant tensor
    mat_circulant = cp.zeros((2*nx, 2*ny, 2*nz, nd), dtype=cp.float_)

    # cube none
    mat_circulant[0:nx, 0:ny, 0:nz, :] = mat[0:nx, 0:ny, 0:nz, :]*sign[0:1, 0:1, 0:1, :]
    # cube x
    mat_circulant[nx+1:2*nx, 0:ny, 0:nz, :] = mat[nx-1:0:-1, 0:ny, 0:nz, :]*sign[1:2, 0:1, 0:1, :]
    # cube y
    mat_circulant[0:nx, ny+1:2*ny, 0:nz, :] = mat[0:nx, ny-1:0:-1, 0:nz, :]*sign[0:1, 1:2, 0:1, :]
    # cube z
    mat_circulant[0:nx, 0:ny, nz+1:2*nz, :] = mat[0:nx, 0:ny, nz-1:0:-1, :]*sign[0:1, 0:1, 1:2, :]
    # cube xy
    mat_circulant[nx+1:2*nx, ny+1:2*ny, 0:nz, :] = mat[nx-1:0:-1, ny-1:0:-1, 0:nz, :]*sign[1:2, 1:2, 0:1, :]
    # cube xz
    mat_circulant[nx+1:2*nx, 0:ny, nz+1:2*nz, :] = mat[nx-1:0:-1, 0:ny, nz-1:0:-1, :]*sign[1:2, 0:1, 1:2, :]
    # cube yz
    mat_circulant[0:nx, ny+1:2*ny, nz+1:2*nz, :] = mat[0:nx, ny-1:0:-1, nz-1:0:-1, :]*sign[0:1, 1:2, 1:2, :]
    # cube xyz
    mat_circulant[nx+1:2*nx, ny+1:2*ny, nz+1:2*nz, :] = mat[nx-1:0:-1, ny-1:0:-1, nz-1:0:-1, :]*sign[1:2, 1:2, 1:2, :]

    # get the FFT of the circulant tensor
    mat_fft = fourier_transform.get_fft_tensor_keep(mat_circulant)

    return mat_fft


def get_prepare(idx_out, idx_in, mat, matrix_type):
    """
    Construct a circulant tensor from a 4D tensor.
    The circulant tensor is constructed for the first 3D.

    The input tensor has the size: (nx, ny, nz, nd).
    The output FFT circulant tensor has the size: (2*nx, 2*ny, 2*nz, nd).
    """

    # get the sign that will be applied to the different blocks of the tensor
    sign = _get_tensor_sign(matrix_type)

    # get the FFT circulant tensor
    mat_fft = _get_tensor_circulant(mat, sign)

    # load the data to the GPU
    if USE_GPU:
        idx_in = cp.asarray(idx_in)
        idx_out = cp.asarray(idx_out)

    # get the indices
    idx_in = cp.unravel_index(idx_in, mat.shape, order="F")
    idx_out = cp.unravel_index(idx_out, mat.shape, order="F")

    return idx_in, idx_out, mat_fft


def get_multiply(idx_out, idx_in, vec_in, mat_fft, scale, matrix_type, flip):
    """
    Matrix-vector multiplication with FFT.
    The matrix is shaped as a FFT circulant tensor.

    The output index vector has the size: n_out.
    The input index vector has the size: n_in.
    The input vector has the size: n_in.
    The input FFT circulant tensor has the size: (2*nx, 2*ny, 2*nz, nd).
    The output vector has the size: n_out.

    For the matrix-vector multiplication is done in several steps:
        - the vector is expanded into a tensor: n_sel to (nx, ny, nz, nd)
        - computation the FFT of the obtained tensor: (nx, ny, nz, nd) to (2*nx, 2*ny, 2*nz, nd)
        - multiplication of FFT circulant tensors: (2*nx, 2*ny, 2*nz, nd)
        - computation the iFFT of the obtained tensor: (2*nx, 2*ny, 2*nz, nd)
        - the tensor is flattened into a vector: (2*nx, 2*ny, 2*nz, nd) to n_sel
    """

    # get the tensor size
    (nx, ny, nz, nd) = mat_fft.shape
    nx = int(nx/2)
    ny = int(ny/2)
    nz = int(nz/2)

    # flip the input and output
    if flip:
        (idx_out, idx_in) = (idx_in, idx_out)

    # load the data to the GPU
    if USE_GPU:
        vec_in = cp.array(vec_in)

    # create a tensor for the vector
    vec_all = cp.zeros((nx, ny, nz, nd), dtype=cp.complex_)

    # assign the elements from the tensor indices
    vec_all[idx_in] = vec_in

    # compute the FFT of the vector (result is the same size as the FFT circulant tensor)
    vec_all_fft = fourier_transform.get_fft_tensor_expand(vec_all)

    # matrix vector multiplication in frequency domain with the FFT circulant tensor
    if matrix_type == "single":
        scale = cp.expand_dims(scale, axis=(0, 1, 2))
        res_all_fft = scale*mat_fft*vec_all_fft
    elif matrix_type == "diag":
        scale = cp.expand_dims(scale, axis=(0, 1, 2))
        res_all_fft = scale*mat_fft*vec_all_fft
    elif matrix_type == "cross":
        res_all_fft = cp.zeros((2*nx, 2*ny, 2*nz, nd), dtype=cp.complex_)
        res_all_fft[:, :, :, 0] = +mat_fft[:, :, :, 2]*vec_all_fft[:, :, :, 1]+mat_fft[:, :, :, 1]*vec_all_fft[:, :, :, 2]
        res_all_fft[:, :, :, 1] = -mat_fft[:, :, :, 2]*vec_all_fft[:, :, :, 0]+mat_fft[:, :, :, 0]*vec_all_fft[:, :, :, 2]
        res_all_fft[:, :, :, 2] = -mat_fft[:, :, :, 1]*vec_all_fft[:, :, :, 0]-mat_fft[:, :, :, 0]*vec_all_fft[:, :, :, 1]
    else:
        raise ValueError("invalid matrix type")

    # compute the iFFT
    res_all = fourier_transform.get_ifft_tensor(res_all_fft)

    # select the elements from the tensor indices
    res_out = res_all[idx_out]

    # unload the data from the GPU
    if USE_GPU:
        res_out = cp.asnumpy(res_out)

    return res_out
