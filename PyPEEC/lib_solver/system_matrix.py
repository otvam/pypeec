"""
Different functions for handling the resistance and inductance matrix.
The resistance matrix is constructed with the non-empty voxels.
The inductance matrix is computed with a FFT circulant tensor.
Thr circulant tensor allows for matrix-vector multiplication with FFT.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np
import scipy.sparse as sps
import scipy.sparse.linalg as sla
from PyPEEC.lib_matrix import matrix_multiply


def _get_face_voxel_indices(n, idx_v, idx_f, A_net, offset):
    # extract the voxel data
    (nx, ny, nz) = n
    nv = nx*ny*nz

    # get the local indices
    idx_local = np.in1d(idx_f, np.arange(offset*nv, (offset+1)*nv))

    # slice matrix (columns)
    A_net = A_net[:, idx_local]

    # get face indices
    nnz = A_net.getnnz(axis=1)
    idx_local = np.flatnonzero(nnz > 0)

    # slice matrix (rows)
    A_net = A_net[idx_local, :]

    # add offset
    idx = offset*nv+idx_v[idx_local]

    return A_net, idx


def _get_face_voxel_matrix(n, idx_v, idx_f, A_net):
    # get the incidence matrix between the faces and voxels
    (A_net_x, idx_x) = _get_face_voxel_indices(n, idx_v, idx_f, A_net, 0)
    (A_net_y, idx_y) = _get_face_voxel_indices(n, idx_v, idx_f, A_net, 1)
    (A_net_z, idx_z) = _get_face_voxel_indices(n, idx_v, idx_f, A_net, 2)

    # assemble incidence matrix and indices
    idx_fv = np.concatenate((idx_x, idx_y, idx_z))
    A_fv_net = sps.block_diag((A_net_x, A_net_y, A_net_z))

    # scale the matrix for flux conversion
    A_fv_net = 0.5*np.abs(A_fv_net)

    return A_fv_net, idx_fv


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


def get_coupling_matrix(n, idx_vc, idx_vm, idx_fc, idx_fm, A_net_c, A_net_m, K_tsr):
    """
    Prepare the matrix for the multiplication:
        - with FFT circulant tensors
        - with dense matrices
    """

    # get the face voxel incidence matrix
    (A_fv_net_c, idx_fvc) = _get_face_voxel_matrix(n, idx_vc, idx_fc, A_net_c)
    (A_fv_net_m, idx_fvm) = _get_face_voxel_matrix(n, idx_vm, idx_fm, A_net_m)

    # get the voxel face incidence matrix
    A_vf_net_c = A_fv_net_c.transpose()
    A_vf_net_m = A_fv_net_m.transpose()

    # get the coupling operator (voxel to voxel)
    K_op_c_tmp = matrix_multiply.get_operator_cross(idx_fvc, idx_fvm, +1*K_tsr)
    K_op_m_tmp = matrix_multiply.get_operator_cross(idx_fvm, idx_fvc, -1*K_tsr)

    # function describing the coupling from the magnetic to the electric faces
    def fct_c(var_f_m):
        var_f_c = A_vf_net_c*K_op_c_tmp(A_fv_net_m*var_f_m)
        return var_f_c

    # function describing the coupling from the electric to the magnetic faces
    def fct_m(var_f_c):
        var_f_m = A_vf_net_m*K_op_m_tmp(A_fv_net_c*var_f_c)
        return var_f_m

    # corresponding linear operator
    K_op_c = sla.LinearOperator((len(idx_fc), len(idx_fm)), matvec=fct_c)
    K_op_m = sla.LinearOperator((len(idx_fm), len(idx_fc)), matvec=fct_m)

    return K_op_c, K_op_m

