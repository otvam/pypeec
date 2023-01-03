import numpy as np


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


def get_source_geometry(src_current, src_voltage):
    # get the indices of the current source voxels
    idx_src_c = np.array([], dtype=np.int64)
    val_src_c = np.array([], dtype=np.complex128)
    for dat_tmp in src_current:
        idx = dat_tmp["idx"]
        value = dat_tmp["value"]

        idx_src_c = np.append(idx_src_c, np.array(idx))
        val_src_c = np.append(val_src_c, np.full(len(idx), value/len(idx)))

    # get the indices of the voltage source voxels
    idx_src_v = np.array([], dtype=np.int64)
    val_src_v = np.array([], dtype=np.complex128)
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


def get_status(n, idx_v, idx_f, idx_src_c, idx_src_v):
    # extract the voxel data
    (nx, ny, nz) = n

    # count
    n_total = nx*ny*nz
    n_conductor = len(idx_v)
    n_faces = len(idx_f)
    n_src = len(idx_src_c)+len(idx_src_v)

    # fraction of voxels
    f_conductor = n_conductor/n_total
    f_src = n_src/n_total

    # assign data
    problem_status = {
        "n_total": n_total,
        "n_conductor": n_conductor,
        "n_faces": n_faces,
        "n_src": n_src,
        "f_conductor": f_conductor,
        "f_src": f_src,
    }

    return problem_status
