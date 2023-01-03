import numpy as np
import scipy.fft as fft


def __get_circulant_tensor(A):
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


def __get_fft_tensor(C):
    # extract the input tensor data
    (nx, ny, nz) = C.shape

    # compute the FFT
    CF = fft.fftn(C, (nx, ny, nz))

    return CF


def get_resistance_matrix(n, d, idx_v, rho_v, idx_f_x, idx_f_y, idx_f_z, idx_f):
    # extract the voxel data
    (nx, ny, nz) = n
    (dx, dy, dz) = d
    n = nx*ny*nz

    # assign the resistivity to a vector with all the voxels (including empty voxels)
    rho_all = np.zeros(n, dtype=np.float64)
    rho_all[idx_v] = rho_v

    # resistance matrix (x-direction)
    R_x = np.zeros(n, dtype=np.float64)
    R_x[idx_f_x] = (dx/(dy*dz))*rho_all[idx_f_x]
    R_x = R_x.reshape((nx, ny, nz), order="F")

    # resistance matrix (y-direction)
    R_y = np.zeros(n, dtype=np.float64)
    R_y[idx_f_y] = (dy/(dx*dz))*rho_all[idx_f_y]
    R_y = R_y.reshape((nx, ny, nz), order="F")

    # resistance matrix (z-direction)
    R_z = np.zeros(n, dtype=np.float64)
    R_z[idx_f_z] = (dz/(dx*dy))*rho_all[idx_f_z]
    R_z = R_z.reshape((nx, ny, nz), order="F")

    # assign the resistance tensor
    R_tensor = np.zeros((nx, ny, nz, 3), dtype=np.float64)
    R_tensor[:, :, :, 0] = R_x
    R_tensor[:, :, :, 1] = R_y
    R_tensor[:, :, :, 2] = R_z

    # assign the matrix as a vector for the preconditioner
    R_vector = R_tensor.flatten(order="F")
    R_vector = R_vector[idx_f]

    return R_tensor, R_vector


def get_inductance_matrix(n, d, idx_f, G_mutual, G_self):
    # extract the voxel data
    (nx, ny, nz) = n
    (dx, dy, dz) = d
    n = nx*ny*nz

    # vacuum permittivity
    mu = 4*np.pi*1e-7

    # compute the circulant tensor
    G_mutual = __get_circulant_tensor(G_mutual)

    # compute the inductance tensor and the FFT
    L_tensor = np.zeros((2*nx, 2*ny, 2*nz, 3), dtype=np.float64)
    L_tensor[:, :, :, 0] = (mu*G_mutual)/(dy**2*dz**2)
    L_tensor[:, :, :, 1] = (mu*G_mutual)/(dx**2*dz**2)
    L_tensor[:, :, :, 2] = (mu*G_mutual)/(dx**2*dy**2)

    # self-inductance for the preconditioner
    L_x = (mu*G_self)/(dy**2*dz**2)
    L_y = (mu*G_self)/(dx**2*dz**2)
    L_z = (mu*G_self)/(dx**2*dy**2)
    L_vector = np.concatenate((L_x*np.ones(n), L_y*np.ones(n), L_z*np.ones(n)), dtype=np.float64)
    L_vector = L_vector[idx_f]

    return L_tensor, L_vector

def get_inductance_operator(n, freq, L_tensor, L_vector):
    # extract the voxel data
    (nx, ny, nz) = n

    # get the angular frequency
    s = 1j*2*np.pi*freq

    # compute the FFT and the impedance
    ZL_tensor = np.zeros((2*nx, 2*ny, 2*nz, 3), dtype=np.complex128)
    for i in range(3):
        ZL_tensor[:, :, :, i] = s*__get_fft_tensor(L_tensor[:, :, :, i])

    # self-impedance for the preconditioner
    ZL_vector = s*L_vector

    return ZL_tensor, ZL_vector
