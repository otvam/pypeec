import numpy as np
import scipy.fft as fft


def get_circulant_tensor(A):
    # extract the input tensor data
    (nx, ny, nz) = A.shape

    # init the circulant tensor
    C = np.zeros((2*nx, 2*ny, 2*nz), dtype=np.float64)

    # cube xyz
    C[0:nx, 0:ny, 0:nz] = A[0:nx, 0:ny, 0:nz]
    # cube x
    C[nx+1:2*nx, 0:ny, 0:nz] = A[nx-1:0:-1, 0:ny, 0:nz]
    # cube y
    C[0:nx, ny+1:2*ny, 0:nz] = A[0:nx, ny-1:0:-1, 0:nz]
    # cube z
    C[0:nx, 0:ny, nz+1:2*nz] = A[0:nx, 0:ny, nz-1:0:-1]
    # cube xy
    C[nx+1:2*nx, ny+1:2*ny, 0:nz] = A[nx-1:0:-1, ny-1:0:-1, 0:nz]
    # cube xz
    C[nx+1:2*nx, 0:ny, nz+1:2*nz] = A[nx-1:0:-1, 0:ny, nz-1:0:-1]
    # cube yz
    C[0:nx, ny+1:2*ny, nz+1:2*nz] = A[0:nx, ny-1:0:-1, nz-1:0:-1]
    # cube xyz
    C[nx+1:2*nx, ny+1:2*ny, nz+1:2*nz] = A[nx-1:0:-1, ny-1:0:-1, nz-1:0:-1]

    return C


def get_fft_tensor(C):
    # extract the input tensor data
    (nx, ny, nz) = C.shape

    # compute the FFT
    CF = fft.fftn(C, (nx, ny, nz))

    return CF


def get_multiply(CF, X):
    # extract the input tensor data
    (nx, ny, nz) = X.shape
    (nnx, nny, nnz) = CF.shape

    # compute the FFT of the vector
    CX = fft.fftn(X, (nnx, nny, nnz))

    # matrix vector multiplication in frequency domain
    CY = CF*CX

    # compute the iFFT
    Y = fft.ifftn(CY)

    # the result is in the first block of the matrix
    Y = Y[0:nx, 0:ny, 0:nz]

    return Y

