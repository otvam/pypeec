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
MATRIX_SPLIT = True
# MATRIX_SPLIT = False

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


def _get_full_cross(mat_fft, res):
    """
    Compute the matrix vector multiplication in frequency domain for the block off-diagonal matrix.
    The product is computed directly and requires additional memory allocation.
    """

    res_tmp = cp.empty(res.shape, dtype=NP_TYPES.COMPLEX)
    res_tmp[:, :, :, 0] = +mat_fft[:, :, :, 2]*res[:, :, :, 1]+mat_fft[:, :, :, 1]*res[:, :, :, 2]
    res_tmp[:, :, :, 1] = -mat_fft[:, :, :, 2]*res[:, :, :, 0]+mat_fft[:, :, :, 0]*res[:, :, :, 2]
    res_tmp[:, :, :, 2] = -mat_fft[:, :, :, 1]*res[:, :, :, 0]-mat_fft[:, :, :, 0]*res[:, :, :, 1]
    res = res_tmp

    return res


def _get_shard_cross(mat_fft, res, matrix_split):
    """
    Compute the matrix vector multiplication in frequency domain for the block off-diagonal matrix.
    The product is computed in chunks, which mitigates the additional memory allocation.
    """

    # get the tensor size
    (nx, ny, nz, nd) = res.shape

    # flatten the tensors
    mat_fft = mat_fft.reshape(nx*ny*nz, nd)
    res = res.reshape((nx*ny*nz, nd))

    # shard the array in different chunks
    idx = cp.linspace(0, nx*ny*nz, matrix_split+1, dtype=NP_TYPES.INT)
    idx = cp.unique(idx)

    # compute the cross product for the different chunks
    for i in range(len(idx)-1):
        # get the indices of the chunk
        idx_tmp = cp.arange(idx[i], idx[i+1])

        # compute the product
        res_tmp = cp.empty((len(idx_tmp), nd), dtype=NP_TYPES.COMPLEX)
        res_tmp[:, 0] = +mat_fft[idx_tmp, 2] * res[idx_tmp, 1] + mat_fft[idx_tmp, 1] * res[idx_tmp, 2]
        res_tmp[:, 1] = -mat_fft[idx_tmp, 2] * res[idx_tmp, 0] + mat_fft[idx_tmp, 0] * res[idx_tmp, 2]
        res_tmp[:, 2] = -mat_fft[idx_tmp, 1] * res[idx_tmp, 0] - mat_fft[idx_tmp, 0] * res[idx_tmp, 1]

        # assign the computed chunk
        res[idx_tmp] = res_tmp

    # reshape the tensor to match the original format
    res = res.reshape((nx, ny, nz, nd))

    return res


def _get_indices(nx, ny, nz, idx, nd_out, dim):
    if dim is None:
        shape = (nx, ny, nz, nd_out)
        idx_mat = cp.unravel_index(idx, (nx, ny, nz, nd_out), order="F")

        idx = {"idx_sel": None, "idx_mat": idx_mat, "shape": shape, "length": len(idx)}
    else:
        nv = nx*ny*nz
        shape = (nx, ny, nz, 1)
        idx_sel = cp.in1d(idx, cp.arange(dim*nv, (dim+1)*nv))
        idx_tmp = idx[idx_sel]-dim*nv
        idx_mat = cp.unravel_index(idx_tmp, shape, order="F")

        idx = {"idx_sel": idx_sel, "idx_mat": idx_mat, "shape": shape, "length": len(idx)}

    return idx


def get_prepare(idx_out, idx_in, mat, matrix_type):
    """
    Construct a circulant tensor from a 4D tensor.
    The circulant tensor is constructed for the first 3D.
    """

    # get tensor size
    (nx, ny, nz, nd) = mat.shape

    # get the memory footprint
    nnz = (2*nx)*(2*ny)*(2*nz)*nd
    itemsize = cp.dtype(NP_TYPES.COMPLEX).itemsize
    footprint = (itemsize*nnz)/(1024**2)

    # display the tensor size
    logger.debug("tensor type: %s" % matrix_type)
    logger.debug("tensor size: (%d, %d, %d)" % (nx, ny, nz))
    logger.debug("tensor footprint: %.3f MB" % footprint)

    # get the sign that will be applied to the different blocks of the tensor
    sign = _get_tensor_sign(matrix_type, nd)

    # load the data to the GPU
    if USE_FFT_GPU:
        mat = cp.asarray(mat)
        idx_in = cp.asarray(idx_in)
        idx_out = cp.asarray(idx_out)

    # get the FFT circulant tensor
    mat_fft = _get_tensor_circulant(mat, sign)

    # get tensor last dimension
    if matrix_type == "single":
        nd_out = 1
    elif matrix_type == "diag":
        nd_out = 3
    elif matrix_type == "cross":
        nd_out = 3
    else:
        raise ValueError("invalid matrix type")

    # length of the output
    n_in = len(idx_in)
    n_out = len(idx_out)

    if MATRIX_SPLIT:
        idx_in_mat = []
        idx_out_mat = []
        for i in range(3):
            idx_in_mat.append(_get_indices(nx, ny, nz, idx_in, nd_out, i))
            idx_out_mat.append(_get_indices(nx, ny, nz, idx_out, nd_out, i))
    else:
        idx_in_mat = _get_indices(nx, ny, nz, idx_in, nd_out, None)
        idx_out_mat = _get_indices(nx, ny, nz, idx_out, nd_out, None)

    return n_in, n_out, idx_in_mat, idx_out_mat, mat_fft


def get_tensor(idx_in, vec_in):
    shape = idx_in["shape"]
    idx_sel = idx_in["idx_sel"]
    idx_mat = idx_in["idx_mat"]

    res = cp.zeros(shape, dtype=NP_TYPES.COMPLEX)
    if idx_sel is None:
        res[idx_mat] = vec_in[:]
    else:
        res[idx_mat] = vec_in[idx_sel]

    return res


def get_vector(idx_out, res):
    length = idx_out["length"]
    idx_sel = idx_out["idx_sel"]
    idx_mat = idx_out["idx_mat"]

    res_out = cp.zeros(length, dtype=NP_TYPES.COMPLEX)
    if idx_sel is None:
        res_out[:] = res[idx_mat]
    else:
        res_out[idx_sel] = res[idx_mat]

    return res_out


def get_combined(idx_in, idx_out, mat_fft, vec_in, matrix_type):
    # assign the elements from the tensor indices
    res = get_tensor(idx_in, vec_in)

    # compute the FFT of the vector (result is the same size as the FFT circulant tensor)
    res = fourier_transform.get_fft_tensor_expand(res, True)

    # matrix vector multiplication in frequency domain with the FFT circulant tensor
    if matrix_type == "single":
        res *= mat_fft
    elif matrix_type == "diag":
        res *= mat_fft
    elif matrix_type == "cross":
        if MATRIX_SPLIT is None:
            res = _get_full_cross(mat_fft, res)
        else:
            res = _get_shard_cross(mat_fft, res, MATRIX_SPLIT)
    else:
        raise ValueError("invalid matrix type")

    # compute the iFFT
    res = fourier_transform.get_ifft_tensor(res, True)

    # select the elements from the tensor indices
    res = get_vector(idx_out, res)

    return res


def get_mult(idx_in, idx_out, mat_fft, vec_in, dim_in, dim_out, dim_mat):
    res = get_tensor(idx_in[dim_in], vec_in)
    res = fourier_transform.get_fft_tensor_expand(res, True)
    res *= mat_fft[:, :, :, [dim_mat]]
    res = fourier_transform.get_ifft_tensor(res, True)
    res = get_vector(idx_out[dim_out], res)

    return res


def get_split(n_out, idx_in, idx_out, mat_fft, vec_in, matrix_type):
    if matrix_type == "single":
        res = get_mult(idx_in, idx_out, mat_fft, vec_in, 0, 0, 0)
    elif matrix_type == "diag":
        res = cp.zeros(n_out, dtype=NP_TYPES.COMPLEX)
        res += get_mult(idx_in, idx_out, mat_fft, vec_in, 0, 0, 0)
        res += get_mult(idx_in, idx_out, mat_fft, vec_in, 1, 1, 0)
        res += get_mult(idx_in, idx_out, mat_fft, vec_in, 2, 2, 0)
    elif matrix_type == "cross":
        res = cp.zeros(n_out, dtype=NP_TYPES.COMPLEX)
        res += get_mult(idx_in, idx_out, mat_fft, vec_in, 1, 0, 2)
        res += get_mult(idx_in, idx_out, mat_fft, vec_in, 2, 0, 1)
        res += get_mult(idx_in, idx_out, mat_fft, vec_in, 0, 1, 2)
        res -= get_mult(idx_in, idx_out, mat_fft, vec_in, 2, 1, 0)
        res -= get_mult(idx_in, idx_out, mat_fft, vec_in, 0, 2, 1)
        res -= get_mult(idx_in, idx_out, mat_fft, vec_in, 1, 2, 0)
    else:
        raise ValueError("invalid matrix type")


    return res

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
    (n_in, n_out, idx_in, idx_out, mat_fft) = data

    # flip the input and output
    if flip:
        (n_out, n_in) = (n_in, n_out)
        (idx_out, idx_in) = (idx_in, idx_out)

    # load the data to the GPU
    if USE_FFT_GPU:
        vec_in = cp.array(vec_in)

    if MATRIX_SPLIT:
        vec_out = get_split(n_out, idx_in, idx_out, mat_fft, vec_in, matrix_type)
    else:
        vec_out = get_combined(idx_in, idx_out, mat_fft, vec_in, matrix_type)

    # unload the data from the GPU
    if USE_FFT_GPU:
        vec_out = cp.asnumpy(vec_out)

    return vec_out


    # res_out = cp.zeros(n_out, dtype=NP_TYPES.COMPLEX)
    #
    # # create a tensor for the vector
    # for i in range(3):
    #     res_tmp = get_tensor(idx_in[i], vec_in)
    #     res_tmp = fourier_transform.get_fft_tensor_expand(res_tmp, True)
    #     res_tmp *= mat_fft
    #     res_tmp = fourier_transform.get_ifft_tensor(res_tmp, True)
    #     res_tmp = get_vector(idx_out[i], res_tmp)
    #
    #     res_out += res_tmp


    # res = cp.zeros(shape, dtype=NP_TYPES.COMPLEX)
    #
    # # assign the elements from the tensor indices
    # res[idx_in] = vec_in
    #
    # # compute the FFT of the vector (result is the same size as the FFT circulant tensor)
    # res = fourier_transform.get_fft_tensor_expand(res, True)
    #
    # # matrix vector multiplication in frequency domain with the FFT circulant tensor
    # if matrix_type == "single":
    #     res *= mat_fft
    # elif matrix_type == "diag":
    #     res *= mat_fft
    # elif matrix_type == "cross":
    #     if MATRIX_SPLIT is None:
    #         res = _get_full_cross(mat_fft, res)
    #     else:
    #         res = _get_shard_cross(mat_fft, res, MATRIX_SPLIT)
    # else:
    #     raise ValueError("invalid matrix type")
    #
    # # compute the iFFT
    # res = fourier_transform.get_ifft_tensor(res, True)
    #
    # # select the elements from the tensor indices
    # res_out = res[idx_out]
    #
    # # unload the data from the GPU
    # if USE_FFT_GPU:
    #     res_out = cp.asnumpy(res_out)
    #
    # return res_out
