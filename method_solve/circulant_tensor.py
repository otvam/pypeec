import numpy as np
import scipy.fft as fft


def get_circulant_tensor(A_in):
    # extract the input tensor data
    (nx, ny, nz) = A_in.shape

    # init the circulant tensor
    C_out = np.zeros((2*nx, 2*ny, 2*nz), dtype=np.float64)

    # cube xyz
    C_out[0:nx, 0:ny, 0:nz] = A_in[0:nx, 0:ny, 0:nz]
    # cube x
    C_out[nx+1:2*nx, 0:ny, 0:nz] = A_in[nx-1:0:-1, 0:ny, 0:nz]
    # cube y
    C_out[0:nx, ny+1:2*ny, 0:nz] = A_in[0:nx, ny-1:0:-1, 0:nz]
    # cube z
    C_out[0:nx, 0:ny, nz+1:2*nz] = A_in[0:nx, 0:ny, nz-1:0:-1]
    # cube xy
    C_out[nx+1:2*nx, ny+1:2*ny, 0:nz] = A_in[nx-1:0:-1, ny-1:0:-1, 0:nz]
    # cube xz
    C_out[nx+1:2*nx, 0:ny, nz+1:2*nz] = A_in[nx-1:0:-1, 0:ny, nz-1:0:-1]
    # cube yz
    C_out[0:nx, ny+1:2*ny, nz+1:2*nz] = A_in[0:nx, ny-1:0:-1, nz-1:0:-1]
    # cube xyz
    C_out[nx+1:2*nx, ny+1:2*ny, nz+1:2*nz] = A_in[nx-1:0:-1, ny-1:0:-1, nz-1:0:-1]

    return C_out


def get_fft_tensor(C_in):
    # extract the input tensor data
    (nx, ny, nz) = C_in.shape

    # compute the FFT
    F_out = fft.fftn(C_in, (nx, ny, nz))

    return F_out

