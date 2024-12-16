"""
Module for doing matrix-vector multiplication (with circulant tensors and FFT).

The multiplication can be done in two ways:
    - combined: the computation is done with the 4D tensors
    - split: the 4D tensors are sliced into several 3D tensors

The "combined" mode is typically faster than the "split" mode.
The "split" mode features a reduced memory footprint.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import scilogger
from pypeec.lib_matrix import fourier_transform

# get a logger
LOGGER = scilogger.get_logger(__name__, "pypeec")

# dummy options
LIBRARY = None
MATRIX_SPLIT = None
USE_FFT_GPU = None
NPCP = None


def _get_tensor_sign(name, nd_in):
    """
    Get the signs for the different tensor blocks composing the circulant tensor.
    """

    if name == "potential":
        sign = NPCP.ones((2, 2, 2, nd_in), dtype=NPCP.float64)
    elif name == "inductance":
        sign = NPCP.ones((2, 2, 2, nd_in), dtype=NPCP.float64)
    elif name == "coupling":
        sign = NPCP.empty((2, 2, 2, nd_in), dtype=NPCP.float64)
        sign[0, 0, 0, :] = NPCP.array([+1, +1, +1], dtype=NPCP.float64)
        sign[1, 0, 0, :] = NPCP.array([-1, +1, +1], dtype=NPCP.float64)
        sign[0, 1, 0, :] = NPCP.array([+1, -1, +1], dtype=NPCP.float64)
        sign[0, 0, 1, :] = NPCP.array([+1, +1, -1], dtype=NPCP.float64)
        sign[1, 1, 0, :] = NPCP.array([-1, -1, +1], dtype=NPCP.float64)
        sign[1, 0, 1, :] = NPCP.array([-1, +1, -1], dtype=NPCP.float64)
        sign[0, 1, 1, :] = NPCP.array([+1, -1, -1], dtype=NPCP.float64)
        sign[1, 1, 1, :] = NPCP.array([-1, -1, -1], dtype=NPCP.float64)
    else:
        raise ValueError("invalid matrix type")

    return sign


def _get_tensor_circulant(mat, sign):
    """
    Construct a circulant tensor from a 4D tensor.
    The circulant tensor is constructed for the first 3D.

    The input tensor has the size: (nx, ny, nz, nd_in).
    The output FFT circulant tensor has the size: (2*nx, 2*ny, 2*nz, nd_in).
    """

    # get the tensor size
    (nx, ny, nz, nd_in) = mat.shape

    # init the circulant tensor
    mat_fft = NPCP.zeros((2 * nx, 2 * ny, 2 * nz, nd_in), dtype=NPCP.float64)

    # cube none
    mat_fft[0:nx, 0:ny, 0:nz, :] = mat[0:nx, 0:ny, 0:nz, :] * sign[0:1, 0:1, 0:1, :]
    # cube x
    mat_fft[nx + 1 : 2 * nx, 0:ny, 0:nz, :] = mat[nx - 1 : 0 : -1, 0:ny, 0:nz, :] * sign[1:2, 0:1, 0:1, :]
    # cube y
    mat_fft[0:nx, ny + 1 : 2 * ny, 0:nz, :] = mat[0:nx, ny - 1 : 0 : -1, 0:nz, :] * sign[0:1, 1:2, 0:1, :]
    # cube z
    mat_fft[0:nx, 0:ny, nz + 1 : 2 * nz, :] = mat[0:nx, 0:ny, nz - 1 : 0 : -1, :] * sign[0:1, 0:1, 1:2, :]
    # cube xy
    mat_fft[nx + 1 : 2 * nx, ny + 1 : 2 * ny, 0:nz, :] = mat[nx - 1 : 0 : -1, ny - 1 : 0 : -1, 0:nz, :] * sign[1:2, 1:2, 0:1, :]
    # cube xz
    mat_fft[nx + 1 : 2 * nx, 0:ny, nz + 1 : 2 * nz, :] = mat[nx - 1 : 0 : -1, 0:ny, nz - 1 : 0 : -1, :] * sign[1:2, 0:1, 1:2, :]
    # cube yz
    mat_fft[0:nx, ny + 1 : 2 * ny, nz + 1 : 2 * nz, :] = mat[0:nx, ny - 1 : 0 : -1, nz - 1 : 0 : -1, :] * sign[0:1, 1:2, 1:2, :]
    # cube xyz
    mat_fft[nx + 1 : 2 * nx, ny + 1 : 2 * ny, nz + 1 : 2 * nz, :] = mat[nx - 1 : 0 : -1, ny - 1 : 0 : -1, nz - 1 : 0 : -1, :] * sign[1:2, 1:2, 1:2, :]

    # get the FFT of the circulant tensor
    mat_fft = fourier_transform.get_fft_tensor_keep(mat_fft, True)

    return mat_fft


def _get_indices(nx, ny, nz, idx, nd_out, dim):
    """
    Get the indices for mapping a vector into a tensor.
    The indices are either computer for all 4D or for a 3D slice.
    """

    if dim is None:
        # shape of the tensor with the vectors (4D)
        shape = (nx, ny, nz, nd_out)

        # mapping between the vector indices and the tensor indices (4D)
        idx_mat = NPCP.unravel_index(idx, (nx, ny, nz, nd_out), order="F")

        # for the case with 4D mapping, all the elements are selected
        idx_sel = None
    else:
        # number of element for the 3D sluce
        nv = nx * ny * nz

        # shape of the tensor with the vectors (4D)
        shape = (nx, ny, nz)

        # indices of the elements included in the considered 3D slices
        idx_sel = NPCP.isin(idx, NPCP.arange(dim * nv, (dim + 1) * nv))

        # mapping between the vector indices and the tensor indices (3D)
        idx_tmp = idx[idx_sel] - dim * nv
        idx_mat = NPCP.unravel_index(idx_tmp, shape, order="F")

    # assign the dict with the indices
    idx = {"idx_sel": idx_sel, "idx_mat": idx_mat, "shape": shape, "length": len(idx)}

    return idx


def _get_tensor(idx, vec):
    """
    Transform a vector into a tensor.
    This is used for the input vector.
    """

    # extract the mapping data
    shape = idx["shape"]
    idx_sel = idx["idx_sel"]
    idx_mat = idx["idx_mat"]

    # init the tensor
    res = NPCP.zeros(shape, dtype=NPCP.complex128)

    # assign the tensor (4D or 3D slice)
    if idx_sel is None:
        res[idx_mat] = vec[:]
    else:
        res[idx_mat] = vec[idx_sel]

    return res


def _get_vector(idx, res):
    """
    Transform a tensor into a vector.
    This is used for the output vector.
    """

    # extract the mapping data
    length = idx["length"]
    idx_sel = idx["idx_sel"]
    idx_mat = idx["idx_mat"]

    # init the vector
    vec = NPCP.zeros(length, dtype=NPCP.complex128)

    # assign the vector (4D or 3D slice)
    if idx_sel is None:
        vec[:] = res[idx_mat]
    else:
        vec[idx_sel] = res[idx_mat]

    return vec


def _get_compute_combined(name, idx_in, idx_out, mat_fft, vec_in):
    """
    Matrix-vector multiplication with FFT.
    The multiplication is done directly with the 4D tensors.

    The output index vector has the size: n_out.
    The input index vector has the size: n_in.
    The input vector has the size: n_in.
    The output vector has the size: n_out.

    The FFT circulant tensor has the size: (2*nx, 2*ny, 2*nz, nd_in).
    The input tensor has the size: (nx, ny, nz, nd_out).

    For the matrix-vector multiplication is done in several steps:
        - the vector is expanded into a tensor: n_in to (nx, ny, nz, nd_out)
        - computation the FFT of the obtained tensor: (nx, ny, nz, nd_out) to (2*nx, 2*ny, 2*nz, nd_out)
        - multiplication of FFT circulant tensors: (2*nx, 2*ny, 2*nz, nd_in) and (2*nx, 2*ny, 2*nz, nd_out)
        - computation the iFFT of the obtained tensor: (2*nx, 2*ny, 2*nz, nd_out)
        - the tensor is flattened into a vector: (2*nx, 2*ny, 2*nz, nd_out) to n_out
    """

    # get the input tensor from the input vector
    res = _get_tensor(idx_in, vec_in)

    # compute the FFT of the input tensor
    res = fourier_transform.get_fft_tensor_expand(res, True)

    # matrix vector multiplication in frequency domain with the FFT circulant tensor
    if name == "potential":
        res *= mat_fft
    elif name == "inductance":
        res *= mat_fft
    elif name == "coupling":
        res_tmp = NPCP.empty(res.shape, dtype=NPCP.complex128)
        res_tmp[:, :, :, 0] = +mat_fft[:, :, :, 2] * res[:, :, :, 1] + mat_fft[:, :, :, 1] * res[:, :, :, 2]
        res_tmp[:, :, :, 1] = -mat_fft[:, :, :, 2] * res[:, :, :, 0] + mat_fft[:, :, :, 0] * res[:, :, :, 2]
        res_tmp[:, :, :, 2] = -mat_fft[:, :, :, 1] * res[:, :, :, 0] - mat_fft[:, :, :, 0] * res[:, :, :, 1]
        res = res_tmp
    else:
        raise ValueError("invalid matrix type")

    # compute the iFFT of the obtained output tensor
    res = fourier_transform.get_ifft_tensor(res, True)

    # extract the output vector from the output tensor
    res = _get_vector(idx_out, res)

    return res


def _get_multiply_slice(idx_in, idx_out, mat_fft, vec_in, dim_in, dim_out, dim_mat):
    """
    Matrix-vector multiplication with FFT.
    The multiplication is done for specific 3D slices composing the 4D tensors.
    """

    # get the input tensor from the input vector
    res = _get_tensor(idx_in[dim_in], vec_in)

    # compute the FFT of the input tensor
    res = fourier_transform.get_fft_tensor_expand(res, True)

    # matrix vector multiplication in frequency domain with the FFT circulant tensor
    res *= mat_fft[:, :, :, dim_mat]

    # compute the iFFT of the obtained output tensor
    res = fourier_transform.get_ifft_tensor(res, True)

    # extract the output vector from the output tensor
    res = _get_vector(idx_out[dim_out], res)

    return res


def _get_compute_split(name, n_out, idx_in, idx_out, mat_fft, vec_in):
    """
    Matrix-vector multiplication with FFT.
    The multiplication is done by splitting the 4D tensor in 3D slices.

    The output index vector has the size: n_out.
    The input index vector has the size: n_in.
    The input vector has the size: n_in.
    The output vector has the size: n_out.

    The FFT circulant tensor has the size: (2*nx, 2*ny, 2*nz, nd_in).
    The input tensor has the size: (nx, ny, nz, nd_out).
    The dimension nd_in and nd_out are used to create the 3D slices.

    For the matrix-vector multiplication is done in several steps for each slice:
        - the vector is expanded into a tensor: n_in to (nx, ny, nz)
        - computation the FFT of the obtained tensor: (nx, ny, nz) to (2*nx, 2*ny, 2*nz)
        - multiplication of FFT circulant tensors: (2*nx, 2*ny, 2*nz) and (2*nx, 2*ny, 2*nz)
        - computation the iFFT of the obtained tensor: (2*nx, 2*ny, 2*nz)
        - the tensor is flattened into a vector: (2*nx, 2*ny, 2*nz) to n_out
    """

    if name == "potential":
        # the multiplication is composed of a single slice
        res = _get_multiply_slice(idx_in, idx_out, mat_fft, vec_in, 0, 0, 0)
    elif name == "inductance":
        # the multiplication is decomposed into three slices
        res = NPCP.zeros(n_out, dtype=NPCP.complex128)
        res += _get_multiply_slice(idx_in, idx_out, mat_fft, vec_in, 0, 0, 0)
        res += _get_multiply_slice(idx_in, idx_out, mat_fft, vec_in, 1, 1, 0)
        res += _get_multiply_slice(idx_in, idx_out, mat_fft, vec_in, 2, 2, 0)
    elif name == "coupling":
        # the multiplication is decomposed into six slices
        res = NPCP.zeros(n_out, dtype=NPCP.complex128)
        res += _get_multiply_slice(idx_in, idx_out, mat_fft, vec_in, 1, 0, 2)
        res += _get_multiply_slice(idx_in, idx_out, mat_fft, vec_in, 2, 0, 1)
        res += _get_multiply_slice(idx_in, idx_out, mat_fft, vec_in, 2, 1, 0)
        res -= _get_multiply_slice(idx_in, idx_out, mat_fft, vec_in, 0, 1, 2)
        res -= _get_multiply_slice(idx_in, idx_out, mat_fft, vec_in, 0, 2, 1)
        res -= _get_multiply_slice(idx_in, idx_out, mat_fft, vec_in, 1, 2, 0)
    else:
        raise ValueError("invalid matrix type")

    return res


def _get_prepare_sub(name, idx_out, idx_in, mat):
    """
    Construct a circulant tensor from a 4D tensor (main function).
    The circulant tensor is constructed along the first 3D.
    The indices for mapping a vector into a tensor are computed.

    The input tensor has the size: (nx, ny, nz, nd_in).
    The output FFT circulant tensor has the size: (2*nx, 2*ny, 2*nz, nd_in).
    """

    # get tensor size
    (nx, ny, nz, nd_in) = mat.shape

    # get the memory footprint
    nnz = (2 * nx) * (2 * ny) * (2 * nz) * nd_in
    itemsize = NPCP.dtype(NPCP.complex128).itemsize
    footprint = (itemsize * nnz) / (1024**2)

    # display the tensor size
    LOGGER.debug("tensor size: (%d, %d, %d)" % (nx, ny, nz))
    LOGGER.debug("tensor footprint: %.2f MB" % footprint)

    # get the sign that will be applied to the different blocks of the tensor
    sign = _get_tensor_sign(name, nd_in)

    # load the data to the GPU
    if USE_FFT_GPU:
        mat = NPCP.asarray(mat)
        idx_in = NPCP.asarray(idx_in)
        idx_out = NPCP.asarray(idx_out)

    # get the FFT circulant tensor
    mat_fft = _get_tensor_circulant(mat, sign)

    # get tensor last dimension
    if name == "potential":
        nd_out = 1
    elif name == "inductance":
        nd_out = 3
    elif name == "coupling":
        nd_out = 3
    else:
        raise ValueError("invalid matrix type")

    # length of the output
    n_in = len(idx_in)
    n_out = len(idx_out)

    # compute the indices for mapping a vector into a tensor
    if MATRIX_SPLIT:
        # the following method is used for the multiplication
        #   - 4D tensor will be sliced into 3D tensors for the computation
        #   - compute the indices for each 3D slice
        idx_in_mat = []
        idx_out_mat = []
        for i in range(nd_out):
            idx_in_mat.append(_get_indices(nx, ny, nz, idx_in, nd_out, i))
            idx_out_mat.append(_get_indices(nx, ny, nz, idx_out, nd_out, i))
    else:
        # the following method is used for the multiplication
        #   - 4D tensor are directly used for the computation
        #   - compute the indices for the 4D tensor
        idx_in_mat = _get_indices(nx, ny, nz, idx_in, nd_out, None)
        idx_out_mat = _get_indices(nx, ny, nz, idx_out, nd_out, None)

    return name, n_in, n_out, idx_in_mat, idx_out_mat, mat_fft


def get_prepare(name, idx_out, idx_in, mat):
    """
    Construct a circulant tensor from a 4D tensor (log wrapper).
    """

    LOGGER.debug("multiplication: %s" % name)
    with LOGGER.BlockIndent():
        data = _get_prepare_sub(name, idx_out, idx_in, mat)

    return data


def set_options(fft_options):
    """
    Assign the options and load the right libray.
    """

    # assign global variable
    global LIBRARY
    global MATRIX_SPLIT
    LIBRARY = fft_options["library"]
    MATRIX_SPLIT = fft_options["matrix_split"]

    # import the right library
    global NPCP
    global USE_FFT_GPU

    if LIBRARY == "CuPy":
        import cupy as lib_tmp

        NPCP = lib_tmp
        USE_FFT_GPU = True
    elif LIBRARY in ["NumPy", "SciPy", "MKL", "FFTW"]:
        import numpy as lib_tmp

        NPCP = lib_tmp
        USE_FFT_GPU = False
    else:
        raise ValueError("invalid FFT library")


def get_multiply(data, vec_in, flip):
    """
    Matrix-vector multiplication with FFT.
    If the flip switch is activated, the input and output are flipped.

    The output index vector has the size: n_out.
    The input index vector has the size: n_in.
    The input vector has the size: n_in.
    The output vector has the size: n_out.
    """

    # extract the data
    (name, n_in, n_out, idx_in, idx_out, mat_fft) = data

    # flip the input and output
    if flip:
        (n_out, n_in) = (n_in, n_out)
        (idx_out, idx_in) = (idx_in, idx_out)

    # load the data to the GPU
    if USE_FFT_GPU:
        vec_in = NPCP.array(vec_in)

    if MATRIX_SPLIT:
        vec_out = _get_compute_split(name, n_out, idx_in, idx_out, mat_fft, vec_in)
    else:
        vec_out = _get_compute_combined(name, idx_in, idx_out, mat_fft, vec_in)

    # unload the data from the GPU
    if USE_FFT_GPU:
        vec_out = NPCP.asnumpy(vec_out)

    return vec_out
