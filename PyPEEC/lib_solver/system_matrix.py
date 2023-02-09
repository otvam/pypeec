"""
Different functions for handling the resistance and inductance matrix.
The resistance matrix is constructed with the non-empty voxels.
The inductance matrix is computed with a FFT circulant tensor.
Thr circulant tensor allows for matrix-vector multiplication with FFT.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np
from PyPEEC.lib_matrix import matrix_multiply


def get_R_vector(n, d, A_net, idx_f, rho_v):
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
    rho_vec = 0.5*rho_v*np.abs(A_net)

    # get the direction of the faces (x, y, z)
    idx_fx = np.in1d(idx_f, np.arange(0*nv, 1*nv))
    idx_fy = np.in1d(idx_f, np.arange(1*nv, 2*nv))
    idx_fz = np.in1d(idx_f, np.arange(2*nv, 3*nv))

    # init the resistance vector
    R_vec = np.zeros(len(rho_vec), dtype=np.float64)

    # resistance vector (different directions)
    R_vec[idx_fx] = (dx/(dy*dz))*rho_vec[idx_fx]
    R_vec[idx_fy] = (dy/(dx*dz))*rho_vec[idx_fy]
    R_vec[idx_fz] = (dz/(dx*dy))*rho_vec[idx_fz]

    return R_vec


def get_L_matrix(n, d, idx_fc, G_self, G_mutual):
    """
    Extract the inductance matrix of the system (used for the full system).

    The voxel structure has the following size: (nx, ny, nz).
    For solving the full system, an inductance tensor is used: (nx, ny, nz, 3).
    """

    # vacuum permeability
    mu = 4*np.pi*1e-7

    # extract the voxel data
    (nx, ny, nz) = n
    (dx, dy, dz) = d
    nv = nx*ny*nz

    # self-inductance for the preconditioner
    L_x = mu*G_self/(dy**2*dz**2)
    L_y = mu*G_self/(dx**2*dz**2)
    L_z = mu*G_self/(dx**2*dy**2)
    L_vec = np.concatenate((L_x*np.ones(nv), L_y*np.ones(nv), L_z*np.ones(nv)))
    L_vec = L_vec[idx_fc]

    # compute the inductance tensor from the Green functions
    L_tsr = np.zeros((nx, ny, nz, 3), dtype=np.float64)
    L_tsr[:, :, :, 0] = mu*G_mutual/(dy**2*dz**2)
    L_tsr[:, :, :, 1] = mu*G_mutual/(dx**2*dz**2)
    L_tsr[:, :, :, 2] = mu*G_mutual/(dx**2*dy**2)

    return L_vec, L_tsr


def get_P_matrix(n, d, idx_vm, G_self, G_mutual):
    """
    Extract the potential matrix of the system.

    The voxel structure has the following size: (nx, ny, nz).
    For solving the preconditioner, a vector is used: n_f.
    For solving the full system, an inductance tensor is used: (nx, ny, nz, 1).
    """

    # vacuum permeability
    mu = 4*np.pi*1e-7

    # extract the voxel data
    (nx, ny, nz) = n
    (dx, dy, dz) = d
    nv = nx*ny*nz

    # self-inductance for the preconditioner
    P_v = G_self/(mu*dx**2*dy**2*dz**2)
    P_vec = P_v*np.ones(nv)
    P_vec = P_vec[idx_vm]

    # compute the inductance tensor from the Green functions
    P_tsr = np.zeros((nx, ny, nz, 1), dtype=np.float64)
    P_tsr[:, :, :, 0] = G_mutual/(mu*dx**2*dy**2*dz**2)

    return P_vec, P_tsr


def get_extract_matrix(idx_fc, idx_vm, L_tsr_c, P_tsr_m):
    """
    Prepare the matrix for the multiplication:
        - with FFT circulant tensors
        - with dense matrices
    """

    L_op_c = matrix_multiply.get_operator_diag(idx_fc, L_tsr_c)
    P_op_m = matrix_multiply.get_operator_single(idx_vm, P_tsr_m)

    return L_op_c, P_op_m


def get_coupling_matrix(idx_fc, idx_fm, K_tsr):
    """
    Prepare the matrix for the multiplication:
        - with FFT circulant tensors
        - with dense matrices
    """

    K_op_c = matrix_multiply.get_operator_cross(idx_fc, idx_fm, +1*K_tsr)
    K_op_m = matrix_multiply.get_operator_cross(idx_fm, idx_fc, -1*K_tsr)

    return K_op_c, K_op_m
