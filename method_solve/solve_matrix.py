import numpy as np


def get_conductor_geometry(conductor):
    # get the indices of the conducting voxels and the resistivity
    idx_c = np.array([], dtype=np.int64)
    rho_c = np.array([], dtype=np.float64)
    for dat_tmp in conductor:
        idx = dat_tmp["idx"]
        rho = dat_tmp["rho"]

        idx_c = np.append(idx_c, np.array(idx))
        rho_c = np.append(rho_c, np.full(len(idx), rho))

    return idx_c, rho_c


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


def get_incidence_matrix(n, A_incidence, idx_c):
    # extract the voxel data
    (nx, ny, nz) = n
    n = nx*ny*nz

    # reduce the size of the incidence matrix (only the considered voxels)
    A_reduced = A_incidence[idx_c, :]

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


def get_resistance_matrix(n, d, idx_c, rho_c, idx_f_x, idx_f_y, idx_f_z, idx_f):
    # extract the voxel data
    (nx, ny, nz) = n
    (dx, dy, dz) = d
    n = nx*ny*nz

    # assign the resistivity to a vector with all the voxels (including empty voxels)
    rho_all = np.zeros(n, dtype=np.float64)
    rho_all[idx_c] = rho_c

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