"""
Different functions for handling the resistance and inductance matrix.
The resistance matrix is constructed with the non-empty voxels.
The inductance matrix is computed with a FFT circulant tensor.
Thr circulant tensor allows for matrix-vector multiplication with FFT.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np


def get_R_vector(n, d, A_red, idx_f, rho_v):
    """
    Extract the resistance vector of the system (diagonal of the resistance matrix).

    The problem contains n_f internal faces.
    The resistance vector has the following length: n_f.
    """

    # extract the voxel data
    (nx, ny, nz) = n
    (dx, dy, dz) = d
    nv = nx*ny*nz

    # get the resistivity of the faces (average between voxels)
    rho_vec = 0.5*rho_v*np.abs(A_red)

    # init the resistance vector
    R_vec = np.zeros(len(rho_vec), dtype=np.float64)

    # get the direction of the faces (x, y, z)
    idx_f_x = np.flatnonzero(np.in1d(idx_f, np.arange(0*nv, 1*nv)))
    idx_f_y = np.flatnonzero(np.in1d(idx_f, np.arange(1*nv, 2*nv)))
    idx_f_z = np.flatnonzero(np.in1d(idx_f, np.arange(2*nv, 3*nv)))

    # resistance vector (different directions)
    R_vec[idx_f_x] = (dx/(dy*dz))*rho_vec[idx_f_x]
    R_vec[idx_f_y] = (dy/(dx*dz))*rho_vec[idx_f_y]
    R_vec[idx_f_z] = (dz/(dx*dy))*rho_vec[idx_f_z]

    return R_vec


def get_L_matrix(n, d, G_mutual):
    """
    Extract the inductance matrix of the system (used for the full system).

    The voxel structure has the following size: (nx, ny, nz).
    For solving the full system, an inductance tensor is used: (nx, ny, nz, 3).
    """

    # extract the voxel data
    (nx, ny, nz) = n
    (dx, dy, dz) = d

    # compute the inductance tensor from the Green functions
    L_tsr = np.zeros((nx, ny, nz, 3), dtype=np.float64)
    L_tsr[:, :, :, 0] = G_mutual/(dy**2*dz**2)
    L_tsr[:, :, :, 1] = G_mutual/(dx**2*dz**2)
    L_tsr[:, :, :, 2] = G_mutual/(dx**2*dy**2)

    return L_tsr


def get_L_vector(n, d, idx_f, G_self):
    """
    Extract the inductance vector of the system (used for the preconditioner).

    The problem contains n_f internal faces.
    For solving the preconditioner, a vector is used: n_f.
    """

    # extract the voxel data
    (nx, ny, nz) = n
    (dx, dy, dz) = d
    nv = nx*ny*nz

    # self-inductance for the preconditioner
    L_x = G_self/(dy**2*dz**2)
    L_y = G_self/(dx**2*dz**2)
    L_z = G_self/(dx**2*dy**2)
    L_vec = np.concatenate((L_x*np.ones(nv), L_y*np.ones(nv), L_z*np.ones(nv)))
    L_vec = L_vec[idx_f]

    return L_vec


def get_P_matrix(n, d, G_mutual):
    """
    Extract the potential matrix of the system (used for the full system).

    The voxel structure has the following size: (nx, ny, nz).
    For solving the full system, an inductance tensor is used: (nx, ny, nz, 1).
    """

    # extract the voxel data
    (nx, ny, nz) = n
    (dx, dy, dz) = d

    # compute the inductance tensor from the Green functions
    P_tsr = np.zeros((nx, ny, nz, 3), dtype=np.float64)
    P_tsr[:, :, :, 0] = G_mutual/(dx**2*dy**2*dz**2)

    return P_tsr


def get_P_vector(n, d, idx_v, G_self):
    """
    Extract the potential vector of the system (used for the preconditioner).

    The problem contains n_f internal faces.
    For solving the preconditioner, a vector is used: n_f.
    """

    # extract the voxel data
    (nx, ny, nz) = n
    (dx, dy, dz) = d
    nv = nx*ny*nz

    # self-inductance for the preconditioner
    P_v = G_self/(dx**2*dy**2*dz**2)
    P_vec = P_v*np.ones(nv)
    P_vec = P_vec[idx_v]

    return P_vec
