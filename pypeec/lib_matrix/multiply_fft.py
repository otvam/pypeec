"""
Module for doing matrix-vector multiplication (with circulant tensors and FFT).

Three different types of matrices are supported:
    - single: tensor representing a simple matrix
        - number of dimensions of the input matrix = 1
        - number of dimensions of the input vector = 1
    - diag: tensor representing a block diagonal matrix
        - number of dimensions of the input matrix = 1
        - number of dimensions of the input vector = 3
    - cross: tensor representing a block off-diagonal matrix
        - number of dimensions of the input matrix = 3
        - number of dimensions of the input vector = 3
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

from pypeec.lib_matrix import fourier_transform
from pypeec.lib_utils import timelogger
from pypeec import config

# get a logger
logger = timelogger.get_logger("FFT")

# get config
NP_TYPES = config.NP_TYPES

# get GPU config
USE_FFT_GPU = config.USE_FFT_GPU

# get number of chunks
MATRIX_SPLIT = config.MATRIX_SPLIT

# load the GPU and CPU libraries
if USE_FFT_GPU:
    import cupy as cp
else:
    import numpy as cp


def _get_tensor_sign(matrix_type, nd):
    """
    Get the signs for the different tensor blocks.
    """

    if matrix_type == "single":
        sign = cp.ones((2, 2, 2, nd), dtype=NP_TYPES.FLOAT)
    elif matrix_type == "diag":
        sign = cp.ones((2, 2, 2, nd), dtype=NP_TYPES.FLOAT)
    elif matrix_type == "cross":
        sign = cp.empty((2, 2, 2, nd), dtype=NP_TYPES.FLOAT)
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
    if USE_FFT_GPU:
        mat = cp.asarray(mat)

    # get the tensor size
    (nx, ny, nz, nd) = mat.shape

    # init the circulant tensor
    mat_fft = cp.zeros((2*nx, 2*ny, 2*nz, nd), dtype=NP_TYPES.FLOAT)

    # cube none
    mat_fft[0:nx, 0:ny, 0:nz, :] = mat[0:nx, 0:ny, 0:nz, :]*sign[0:1, 0:1, 0:1, :]
    # cube x
    mat_fft[nx+1:2*nx, 0:ny, 0:nz, :] = mat[nx-1:0:-1, 0:ny, 0:nz, :]*sign[1:2, 0:1, 0:1, :]
    # cube y
    mat_fft[0:nx, ny+1:2*ny, 0:nz, :] = mat[0:nx, ny-1:0:-1, 0:nz, :]*sign[0:1, 1:2, 0:1, :]
    # cube z
    mat_fft[0:nx, 0:ny, nz+1:2*nz, :] = mat[0:nx, 0:ny, nz-1:0:-1, :]*sign[0:1, 0:1, 1:2, :]
    # cube xy
    mat_fft[nx+1:2*nx, ny+1:2*ny, 0:nz, :] = mat[nx-1:0:-1, ny-1:0:-1, 0:nz, :]*sign[1:2, 1:2, 0:1, :]
    # cube xz
    mat_fft[nx+1:2*nx, 0:ny, nz+1:2*nz, :] = mat[nx-1:0:-1, 0:ny, nz-1:0:-1, :]*sign[1:2, 0:1, 1:2, :]
    # cube yz
    mat_fft[0:nx, ny+1:2*ny, nz+1:2*nz, :] = mat[0:nx, ny-1:0:-1, nz-1:0:-1, :]*sign[0:1, 1:2, 1:2, :]
    # cube xyz
    mat_fft[nx+1:2*nx, ny+1:2*ny, nz+1:2*nz, :] = mat[nx-1:0:-1, ny-1:0:-1, nz-1:0:-1, :]*sign[1:2, 1:2, 1:2, :]

    # get the FFT of the circulant tensor
    mat_fft = fourier_transform.get_fft_tensor_keep(mat_fft, True)

    return mat_fft


def get_prepare(idx_out, idx_in, mat, matrix_type):
    """
    Construct a circulant tensor from a 4D tensor.
    The circulant tensor is constructed for the first 3D.
    """

    # get tensor size
    (nx, ny, nz, nd) = mat.shape

    # get tensor last dimension
    if matrix_type == "single":
        nd_out = 1
    elif matrix_type == "diag":
        nd_out = 3
    elif matrix_type == "cross":
        nd_out = 3
    else:
        raise ValueError("invalid matrix type")

    # get the memory footprint
    nnz = (2*nx)*(2*ny)*(2*nz)*(nd+nd_out)
    itemsize = cp.dtype(NP_TYPES.COMPLEX).itemsize
    footprint = (itemsize*nnz)/(1024**2)

    # display the tensor size
    logger.debug("tensor type: %s" % matrix_type)
    logger.debug("tensor size: (%d, %d, %d)" % (nx, ny, nz))
    logger.debug("tensor footprint: %.3f MB" % footprint)

    # get the sign that will be applied to the different blocks of the tensor
    sign = _get_tensor_sign(matrix_type, nd)

    # get the FFT circulant tensor
    mat_fft = _get_tensor_circulant(mat, sign)

    # load the data to the GPU
    if USE_FFT_GPU:
        idx_in = cp.asarray(idx_in)
        idx_out = cp.asarray(idx_out)

    # get the indices
    shape = [nx, ny, nz, nd_out]
    shape_fft = [2*nx, 2*ny, 2*nz, nd_out]
    idx_in = cp.unravel_index(idx_in, shape, order="F")
    idx_out = cp.unravel_index(idx_out,  shape, order="F")

    return shape, shape_fft, idx_in, idx_out, mat_fft


def get_multiply(data, vec_in, matrix_type, flip):
    """
    Matrix-vector multiplication with FFT.
    If the flip switch is activated, the input and output are flipped.

    The output index vector has the size: n_out.
    The input index vector has the size: n_in.
    The input vector has the size: n_in.
    The input FFT circulant tensor has the size: (2*nx, 2*ny, 2*nz, nd_int).
    The output vector has the size: n_out.

    For the matrix-vector multiplication is done in several steps:
        - the vector is expanded into a tensor: n_in to (nx, ny, nz, nd_out)
        - computation the FFT of the obtained tensor: (nx, ny, nz, nd_out) to (2*nx, 2*ny, 2*nz, nd_out)
        - multiplication of FFT circulant tensors: (2*nx, 2*ny, 2*nz, nd_int) and (2*nx, 2*ny, 2*nz, nd_out)
        - computation the iFFT of the obtained tensor: (2*nx, 2*ny, 2*nz, nd_out)
        - the tensor is flattened into a vector: (2*nx, 2*ny, 2*nz, nd_out) to n_out
    """

    # extract data
    (shape, shape_fft, idx_in, idx_out, mat_fft) = data

    # flip the input and output
    if flip:
        (idx_out, idx_in) = (idx_in, idx_out)

    # load the data to the GPU
    if USE_FFT_GPU:
        vec_in = cp.array(vec_in)

    # create a tensor for the vector
    res = cp.zeros(shape, dtype=NP_TYPES.COMPLEX)

    # assign the elements from the tensor indices
    res[idx_in] = vec_in

    # compute the FFT of the vector (result is the same size as the FFT circulant tensor)
    res = fourier_transform.get_fft_tensor_expand(res, True)

    # matrix vector multiplication in frequency domain with the FFT circulant tensor
    if matrix_type == "single":
        res *= mat_fft
    elif matrix_type == "diag":
        res *= mat_fft
    elif matrix_type == "cross":
        res_tmp = cp.zeros(shape_fft, dtype=NP_TYPES.COMPLEX)
        res_tmp[:, :, :, 0] = +mat_fft[:, :, :, 2]*res[:, :, :, 1]+mat_fft[:, :, :, 1]*res[:, :, :, 2]
        res_tmp[:, :, :, 1] = -mat_fft[:, :, :, 2]*res[:, :, :, 0]+mat_fft[:, :, :, 0]*res[:, :, :, 2]
        res_tmp[:, :, :, 2] = -mat_fft[:, :, :, 1]*res[:, :, :, 0]-mat_fft[:, :, :, 0]*res[:, :, :, 1]
        res = res_tmp
    else:
        raise ValueError("invalid matrix type")

    # compute the iFFT
    res = fourier_transform.get_ifft_tensor(res, True)

    # select the elements from the tensor indices
    res_out = res[idx_out]

    # unload the data from the GPU
    if USE_FFT_GPU:
        res_out = cp.asnumpy(res_out)

    return res_out
