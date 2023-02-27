"""
Different functions for handling creating the PEEC dense matrices:
    - resistance matrix
    - inductance and potential matrix
    - magnetic-electric coupling matrices

Function operators are returned for performing the matrix-vector multiplications.
The multiplication can either be done with the dense matrices or with FFT circulant tensors.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import numpy as np
import scipy.sparse as sps
from pypeec.lib_matrix import matrix_multiply


def _get_face_voxel_indices(n, idx_v, idx_f, A_net, offset):
    """
    Create a matrix to project a variable into a voxel variable.
    The variable is a vector and a single component (x, y, or z) is projected.
    Create an index vector for the non-zero voxel vector components.
    """

    # extract the voxel data
    (nx, ny, nz) = n
    nv = nx*ny*nz

    # get the local indices (face indices of the incidence matrix)
    idx_local = np.in1d(idx_f, np.arange(offset*nv, (offset+1)*nv))

    # slice matrix (columns)
    A_net = A_net[:, idx_local]

    # get face indices (get the non-zero entry of the projected voxel variable)
    nnz = A_net.getnnz(axis=1)
    idx_local = np.flatnonzero(nnz > 0)

    # slice matrix (rows)
    A_net = A_net[idx_local, :]

    # scale the matrix for vector projection
    A_net = 0.5*np.abs(A_net)

    # add index offset (such that the x, z, and z indices are not identical)
    idx = offset*nv+idx_v[idx_local]

    return A_net, idx


def _get_face_voxel_matrix(n, idx_v, idx_f, A_net):
    """
    Create a matrix to project a face vector into a voxel vector.
    All the vector components (x, y, and z) are projected.
    Create an index vector for the non-zero voxel vector components.
    """

    # get the incidence matrix between the faces and voxels
    (A_net_x, idx_x) = _get_face_voxel_indices(n, idx_v, idx_f, A_net, 0)
    (A_net_y, idx_y) = _get_face_voxel_indices(n, idx_v, idx_f, A_net, 1)
    (A_net_z, idx_z) = _get_face_voxel_indices(n, idx_v, idx_f, A_net, 2)

    # assemble incidence matrix and indices
    idx_fv = np.concatenate((idx_x, idx_y, idx_z))
    A_fv_net = sps.block_diag((A_net_x, A_net_y, A_net_z))

    return A_fv_net, idx_fv


def _get_operator_zeros(idx_out):
    """
    Get a linear operator returning zeros.
    """

    # function returning zeros
    def op(_):
        var_out = np.zeros(len(idx_out), dtype=np.complex_)
        return var_out

    return op


def get_R_vector(n, d, A_net, idx_f, rho_v, has_domain):
    """
    Extract the resistance vector of the system (diagonal of the resistance matrix).

    The problem contains n_f internal faces.
    The resistance vector has the following length: n_f.
    """

    # check if the vector is required
    if not has_domain:
        R_vec = np.zeros(len(idx_f), dtype=np.complex_)
        return R_vec

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
    R_vec = np.zeros(len(rho_vec), dtype=np.complex_)

    # resistance vector (different directions)
    R_vec[idx_fx] = (dx/(dy*dz))*rho_vec[idx_fx]
    R_vec[idx_fy] = (dy/(dx*dz))*rho_vec[idx_fy]
    R_vec[idx_fz] = (dz/(dx*dy))*rho_vec[idx_fz]

    return R_vec


def get_L_matrix(n, d, idx_f, G_self, G_mutual, has_domain):
    """
    Extract the inductance matrix of the system (used for the full system).

    The problem contains n_f internal faces.
    The voxel structure has the following size: (nx, ny, nz).
    The green tensor has the following size: (nx, ny, nz).

    The green tensor is transformed into an inductance tensor: (nx, ny, nz, 3).
    The tensor is then used to create a matrix-vector linear operator:
        - input size: n_f
        - output size: n_f
    """

    # check if the matrix is required
    if not has_domain:
        L_vec = np.zeros(len(idx_f), dtype=np.float_)
        L_op = _get_operator_zeros(idx_f)
        return L_vec, L_op

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
    L_vec = L_vec[idx_f]

    # compute the inductance tensor from the Green functions
    L_tsr = np.zeros((nx, ny, nz, 3), dtype=np.float_)
    L_tsr[:, :, :, 0] = mu*G_mutual/(dy**2*dz**2)
    L_tsr[:, :, :, 1] = mu*G_mutual/(dx**2*dz**2)
    L_tsr[:, :, :, 2] = mu*G_mutual/(dx**2*dy**2)

    # get the matrix-vector operator
    L_op = matrix_multiply.get_operator_diag(idx_f, L_tsr)

    return L_vec, L_op


def get_P_matrix(n, d, idx_v, G_self, G_mutual, has_domain):
    """
    Extract the potential matrix of the system.

    The problem contains n_v non-empty voxels.
    The voxel structure has the following size: (nx, ny, nz).
    The green tensor has the following size: (nx, ny, nz).

    The green tensor is transformed into a potential tensor: (nx, ny, nz, 1).
    The tensor is then used to create a matrix-vector linear operator:
        - input size: n_v
        - output size: n_v
    """

    # check if the matrix is required
    if not has_domain:
        P_vec = np.zeros(len(idx_v), dtype=np.float_)
        P_op = _get_operator_zeros(idx_v)
        return P_vec, P_op

    # vacuum permeability
    mu = 4*np.pi*1e-7

    # extract the voxel data
    (nx, ny, nz) = n
    (dx, dy, dz) = d
    nv = nx*ny*nz

    # self-inductance for the preconditioner
    P_v = G_self/(mu*dx**2*dy**2*dz**2)
    P_vec = P_v*np.ones(nv)
    P_vec = P_vec[idx_v]

    # compute the inductance tensor from the Green functions
    P_tsr = np.zeros((nx, ny, nz, 1), dtype=np.float_)
    P_tsr[:, :, :, 0] = G_mutual/(mu*dx**2*dy**2*dz**2)

    # get the matrix-vector operator
    P_op = matrix_multiply.get_operator_single(idx_v, P_tsr)

    return P_vec, P_op


def get_coupling_matrix(n, idx_vc, idx_vm, idx_fc, idx_fm, A_net_c, A_net_m, K_tsr, has_coupling):
    """
    Extract the magnetic-electric coupling matrices.

    The problem contains n_fc internal electric faces.
    The problem contains n_fm internal magnetic faces.
    The voxel structure has the following size: (nx, ny, nz).
    The coupling tensor has the following size: (nx, ny, nz, 3).

    Ideally, the coupling matrix would directly operate between the faces.
    The face to face coupling matrix is not a Toeplitz matrix with Toeplitz blocks.
    The voxel to voxel coupling matrix is a Toeplitz matrix with Toeplitz blocks.
    Therefore, the following procedure is used:
        - the face vector is projected into a voxel vector
        - the multiplication is done with the coupling tensor
        - voxel vector is projected into a face vector

    It should be noted that this projection has a negative impact on the achieved accuracy.
    However, this step is currently required for obtaining Toeplitz matrices.

    For the electric coupling, the matrix-vector linear operator has the following size:
        - input size: n_fm
        - output size: n_fc

    For the magnetic coupling, the matrix-vector linear operator has the following size:
        - input size: n_fc
        - output size: n_fm
    """

    # check if the matrix is required
    if not has_coupling:
        K_op_c = _get_operator_zeros(idx_fc)
        K_op_m = _get_operator_zeros(idx_fm)
        return K_op_c, K_op_m

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
    def K_op_c(var_f_m):
        var_f_c = A_vf_net_c*K_op_c_tmp(A_fv_net_m*var_f_m)
        return var_f_c

    # function describing the coupling from the electric to the magnetic faces
    def K_op_m(var_f_c):
        var_f_m = A_vf_net_m*K_op_m_tmp(A_fv_net_c*var_f_c)
        return var_f_m

    return K_op_c, K_op_m
