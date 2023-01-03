import numpy as np


def get_sol_extract(n, idx_f, idx_v, idx_src_v, sol):
    # extract the voxel data
    (nx, ny, nz) = n
    n_v = len(idx_v)
    n_f = len(idx_f)
    n_src_v = len(idx_src_v)
    n = nx*ny*nz

    # assign face currents
    I_face = np.zeros(3*n, dtype=np.complex128)
    I_face[idx_f] = sol[0:n_f]

    # assign voxel voltages
    V_voxel = np.zeros(n, dtype=np.complex128)
    V_voxel[idx_v] = sol[n_f:n_f+n_v]

    # assign voltage source currents
    I_src_v = np.zeros(n, dtype=np.complex128)
    I_src_v[idx_src_v] = sol[n_f+n_v:n_f+n_v+n_src_v]

    return I_face, V_voxel, I_src_v


def get_current_density(n, d, A_incidence, I_face):
    # extract the voxel data
    (nx, ny, nz) = n
    (dx, dy, dz) = d
    n = nx*ny*nz

    # project the face currents into the voxels
    I_x = 0.5 * np.abs(A_incidence[:, 0:n]) * I_face[0:n]
    I_y = 0.5 * np.abs(A_incidence[:, n:2*n]) * I_face[n:2*n]
    I_z = 0.5 * np.abs(A_incidence[:, 2*n:3*n]) * I_face[2*n:3*n]

    # convert currents into current densities
    J_x = I_x/(dy*dz)
    J_y = I_y/(dx*dz)
    J_z = I_z/(dx*dy)

    # assemble voxel current densities
    J_voxel = np.stack((J_x, J_y, J_z), axis=1, dtype=np.complex128)

    return J_voxel

