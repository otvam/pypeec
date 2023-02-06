"""
Module for doing matrix-vector multiplication (with circulant tensors and FFT).
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np
from PyPEEC.lib_matrix import fourier_transform


def _get_prepare_vector(nx, ny, nz, nd, idx_sel, vec_sel):
    """
    Prepare a vector for the circulant FFT multiplication.
    """

    # expand the vector into a vector with all the dimention
    vec_all = np.zeros(nx*ny*nz*nd, dtype=np.complex128)
    vec_all[idx_sel] = vec_sel

    # reshape the vector into a tensor
    vec_all = vec_all.reshape((nx, ny, nz, nd), order="F")

    return vec_all


def _get_extract_vector(idx_sel, vec_all):
    """
    Extract a vector from the circulant FFT multiplication result.
    """

    # flatten the tensor into a vector
    vec_all = vec_all.flatten(order="F")

    # select the elements
    res_sel = vec_all[idx_sel]

    return res_sel


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
    mat_circulant = np.zeros((2*nx, 2*ny, 2*nz, nd), dtype=np.float64)

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
    mat_fft = fourier_transform.get_fft_tensor(mat_circulant, False)

    return mat_fft


def get_prepare(mat, matrix_type):

    if matrix_type == "3D":
        sign = np.ones((2, 2, 2, 1), dtype=np.int64)
    elif matrix_type == "4D_diag":
        sign = np.ones((2, 2, 2, 3), dtype=np.int64)
    elif matrix_type == "4D_off":
        sign = np.empty((2, 2, 2, 3), dtype=np.int64)
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

    mat_fft = _get_tensor_circulant(mat, sign)

    return mat_fft


def get_multiply(idx_sel, vec_sel, mat_fft, matrix_type):
    """
    Matrix-vector multiplication with FFT.
    The matrix is shaped as a FFT circulant tensor.

    The index vector has the size: n_sel.
    The input vector has the size: n_sel.
    The input FFT circulant tensor has the size: (2*nx, 2*ny, 2*nz, nd).
    The output vector has the size: n_sel.

    For the matrix-vector multiplication is done in several steps:
        - the vector is expanded into a tensor: n_sel to (nx, ny, nz, nd)
        - computation the FFT of the obtained tensor: (nx, ny, nz, nd) to (2*nx, 2*ny, 2*nz, nd)
        - multiplication of FFT circulant tensors: (2*nx, 2*ny, 2*nz, nd)
        - computation the iFFT of the obtained tensor: (2*nx, 2*ny, 2*nz, nd)
        - shrinking of the obtained tensor: (2*nx, 2*ny, 2*nz, nd) to (nx, ny, nz, nd)
        - the tensor is flattened into a vector: (nx, ny, nz, nd) to n_sel
    """

    # get the tensor size
    (nx, ny, nz, nd) = mat_fft.shape
    nx = int(nx/2)
    ny = int(ny/2)
    nz = int(nz/2)

    # prepare the vector (transform the vector into a tensor)
    vec_all = _get_prepare_vector(nx, ny, nz, nd, idx_sel, vec_sel)

    # compute the FFT of the vector (result is the same size as the FFT circulant tensor)
    vec_all_fft = fourier_transform.get_fft_tensor(vec_all, True)

    # init the results
    res_all_fft = np.zeros((2*nx, 2*ny, 2*nz, nd), dtype=np.complex128)

    # matrix vector multiplication in frequency domain with the FFT circulant tensor
    if matrix_type == "3D":
        res_all_fft[:, :, :, 0] = mat_fft[:, :, :, 0]*vec_all_fft[:, :, :, 0]
    elif matrix_type == "4D_diag":
        res_all_fft[:, :, :, 0] = mat_fft[:, :, :, 0]*vec_all_fft[:, :, :, 0]
        res_all_fft[:, :, :, 1] = mat_fft[:, :, :, 1]*vec_all_fft[:, :, :, 1]
        res_all_fft[:, :, :, 2] = mat_fft[:, :, :, 2]*vec_all_fft[:, :, :, 2]
    elif matrix_type == "4D_off":
        res_all_fft[:, :, :, 0] = +mat_fft[:, :, :, 2]*vec_all_fft[:, :, :, 1]+mat_fft[:, :, :, 1]*vec_all_fft[:, :, :, 2]
        res_all_fft[:, :, :, 1] = -mat_fft[:, :, :, 2]*vec_all_fft[:, :, :, 0]+mat_fft[:, :, :, 0]*vec_all_fft[:, :, :, 2]
        res_all_fft[:, :, :, 2] = -mat_fft[:, :, :, 1]*vec_all_fft[:, :, :, 0]-mat_fft[:, :, :, 0]*vec_all_fft[:, :, :, 1]
    else:
        raise ValueError("invalid matrix type")

    # compute the iFFT
    res_all = fourier_transform.get_ifft_tensor(res_all_fft, False)

    # the result is in the first block of the matrix
    res_all = res_all[0:nx, 0:ny, 0:nz, :]

    # extract the vector (transform the tensor into a vector)
    res_sel = _get_extract_vector(idx_sel, res_all)

    return res_sel
