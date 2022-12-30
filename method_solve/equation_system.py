import numpy as np
from method_solve import circulant_tensor

def get_conductor_geometry(conductor):
    # get the indices of the conducting voxels and the resistivity
    idx_v = np.array([], dtype=np.int64)
    rho_v = np.array([], dtype=np.float64)
    for dat_tmp in conductor:
        idx = dat_tmp["idx"]
        rho = dat_tmp["rho"]

        idx_v = np.append(idx_v, np.array(idx))
        rho_v = np.append(rho_v, np.full(len(idx), rho))

    return idx_v, rho_v


def get_source_geomtry(src_current, src_voltage):

    # get the indices of the current source voxels
    idx_src_c = np.array([], dtype=np.int64)
    val_src_c = np.array([], dtype=np.float64)
    for dat_tmp in src_current:
        idx = dat_tmp["idx"]
        value = dat_tmp["value"]

        idx_src_c = np.append(idx_src_c, np.array(idx))
        val_src_c = np.append(val_src_c, np.full(len(idx), value/len(idx)))

    # get the indices of the voltage source voxels
    idx_src_v = np.array([], dtype=np.int64)
    val_src_v = np.array([], dtype=np.float64)
    for dat_tmp in src_voltage:
        idx = dat_tmp["idx"]
        value = dat_tmp["value"]

        idx_src_v = np.append(idx_src_v, np.array(idx))
        val_src_v = np.append(val_src_v, np.full(len(idx), value))

    return idx_src_c, val_src_c, idx_src_v, val_src_v


def get_source_index(n, idx_v, idx_src_c, idx_src_v):
    # extract the voxel data
    (nx, ny, nz) = n
    n_v = len(idx_v)
    n = nx*ny*nz

    # get the local indices for the current source
    idx_tmp = np.zeros(n, dtype=np.int64)
    idx_tmp[idx_v] = np.arange(n_v, dtype=np.int64)
    idx_src_c_local = idx_tmp[idx_src_c]

    # get the local indices for the voltage source
    idx_tmp = np.zeros(n, dtype=np.int64)
    idx_tmp[idx_v] = np.arange(n_v, dtype=np.int64)
    idx_src_v_local = idx_tmp[idx_src_v]

    return idx_src_c_local, idx_src_v_local


def get_incidence_matrix(n, A_incidence, idx_v):
    # extract the voxel data
    (nx, ny, nz) = n
    n = nx*ny*nz

    # reduce the size of the incidence matrix (only the considered voxels)
    A_reduced = A_incidence[idx_v, :]

    # indices of the x-oriented faces (local face indices)
    idx_f_x = np.sum(np.abs(A_reduced[:, 0:n]), axis=0) == 2
    idx_f_x = np.flatnonzero(idx_f_x)

    # indices of the y-oriented faces (local face indices)
    idx_f_y = np.sum(np.abs(A_reduced[:, n:2*n]), axis=0) == 2
    idx_f_y = np.flatnonzero(idx_f_y)

    # indices of the z-oriented faces (local face indices)
    idx_f_z = np.sum(np.abs(A_reduced[:, 2*n:3*n]), axis=0) == 2
    idx_f_z = np.flatnonzero(idx_f_z)

    # indices of the all the internal faces (global face indices)
    idx_f = np.sum(np.abs(A_reduced), axis=0) == 2
    idx_f = np.flatnonzero(idx_f)

    # reduce the size of the incidence matrix (only the considered faces)
    A_reduced = A_reduced[:, idx_f]

    return A_reduced, idx_f_x, idx_f_y, idx_f_z, idx_f


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
    G_mutual = circulant_tensor.get_circulant_tensor(G_mutual)

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
    ZL_tensor[:, :, :, 0] = s*circulant_tensor.get_fft_tensor(L_tensor[:, :, :, 0])
    ZL_tensor[:, :, :, 1] = s*circulant_tensor.get_fft_tensor(L_tensor[:, :, :, 1])
    ZL_tensor[:, :, :, 2] = s*circulant_tensor.get_fft_tensor(L_tensor[:, :, :, 2])

    # self-impedance for the preconditioner
    ZL_vector = s*L_vector

    return ZL_tensor, ZL_vector


def get_source_vector(idx_v, idx_f, idx_src_c_local, val_src_c, val_src_v):
    # extract the voxel data
    n_v = len(idx_v)
    n_f = len(idx_f)

    # no excitation for the voltage law
    b_src_zero = np.zeros(n_f, dtype=np.float64)

    # current sources are connected to the current law
    b_src_current = np.zeros(n_v, dtype=np.float64)
    b_src_current[idx_src_c_local] = val_src_c

    # voltage sources are separate equations
    b_src_voltage = val_src_v

    # assemble
    b_src = np.concatenate((b_src_zero, b_src_current, b_src_voltage), dtype=np.float64)

    return b_src
