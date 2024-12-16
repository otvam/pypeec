"""
Different functions for handling creating the PEEC dense matrices:
    - inductance and potential matrix
    - magnetic-electric coupling matrices

Function operators are returned for performing the matrix-vector multiplications.
The multiplication can either be done with the dense matrices or with FFT circulant tensors.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import numpy as np
import scipy.sparse as sps
import scipy.constants as cst
from pypeec.lib_matrix import matrix_multiply


def _get_face_voxel_indices(n, idx_v, idx_f, A_net, offset):
    """
    Create a matrix to project a variable into a voxel variable.
    The variable is a vector and a single component (x, y, or z) is projected.
    Create an index vector for the non-zero voxel vector components.
    """

    # get total size
    nv = np.prod(n)

    # get the local indices (face indices of the incidence matrix)
    idx_local = np.isin(idx_f, np.arange(offset * nv, (offset + 1) * nv, dtype=np.int64))

    # slice matrix (columns)
    A_net = A_net[:, idx_local]

    # get face indices (get the non-zero entry of the projected voxel variable)
    idx_local = A_net.getnnz(axis=1) > 0

    # slice matrix (rows)
    A_net = A_net[idx_local, :]

    # scale the matrix for vector projection
    A_net = 0.5 * np.abs(A_net)

    # extract the indices
    idx = idx_v[idx_local]

    # add index offset (such that the x, z, and z indices are not identical)
    idx = offset * nv + idx

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

    # vector with zeros
    var_out = np.zeros(len(idx_out), dtype=np.complex128)

    # function returning zeros
    def op(_):
        return var_out

    return op


def get_inductance_matrix(n, d, idx_f, G_self, G_mutual, mult_type):
    """
    Extract the inductance matrix of the system (used for the full system).

    The problem contains n_f internal faces.
    The voxel structure has the following size: (nx, ny, nz).
    The green tensor has the following size: (nx, ny, nz, 1).

    The tensor is then used to create a matrix-vector linear operator:
        - input size: n_f
        - output size: n_f
    """

    # check if the matrix is required
    if len(idx_f) == 0:
        # dummy diagonal coefficient
        L = np.nan

        # dummy matrix multiplication operator
        L_op = _get_operator_zeros(idx_f)

        return L, L_op

    # extract the voxel data
    (dx, dy, dz) = d

    # get total size
    nv = np.prod(n)

    # get the direction of the faces (x, y, z)
    idx_fx = np.isin(idx_f, np.arange(0 * nv, 1 * nv, dtype=np.int64))
    idx_fy = np.isin(idx_f, np.arange(1 * nv, 2 * nv, dtype=np.int64))
    idx_fz = np.isin(idx_f, np.arange(2 * nv, 3 * nv, dtype=np.int64))

    # scaling factor
    scale = np.zeros(len(idx_f), dtype=np.complex128)
    scale[idx_fx] = cst.mu_0 / (dy**2 * dz**2)
    scale[idx_fy] = cst.mu_0 / (dx**2 * dz**2)
    scale[idx_fz] = cst.mu_0 / (dx**2 * dy**2)

    # self-inductance for the preconditioner (diagonal coefficient)
    L = scale * G_self

    # get the matrix-vector operator
    L_op_tmp = matrix_multiply.get_operator_inductance(idx_f, G_mutual, mult_type)

    # function describing the inductance matrix multiplication
    def L_op(var_f):
        res_f = scale * L_op_tmp(var_f)
        return res_f

    return L, L_op


def get_potential_matrix(d, idx_v, G_self, G_mutual, mult_type):
    """
    Extract the potential matrix of the system.

    The problem contains n_v non-empty voxels.
    The voxel structure has the following size: (nx, ny, nz).
    The green tensor has the following size: (nx, ny, nz, 1).

    The tensor is then used to create a matrix-vector linear operator:
        - input size: n_v
        - output size: n_v
    """

    # check if the matrix is required
    if len(idx_v) == 0:
        # dummy diagonal coefficient
        P = np.nan

        # dummy matrix multiplication operator
        P_op = _get_operator_zeros(idx_v)

        return P, P_op

    # extract the voxel data
    (dx, dy, dz) = d

    # scaling factor
    scale = 1 / (cst.mu_0 * dx**2 * dy**2 * dz**2)

    # self-potential for the preconditioner (diagonal coefficient)
    P = scale * G_self

    # get the matrix-vector operator
    P_op_tmp = matrix_multiply.get_operator_potential(idx_v, G_mutual, mult_type)

    # function describing the potential matrix multiplication
    def P_op(var_v):
        res_v = scale * P_op_tmp(var_v)
        return res_v

    return P, P_op


def get_coupling_matrix(n, idx_vc, idx_vm, idx_fc, idx_fm, A_net_c, A_net_m, K_tsr, mult_type):
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
    if (len(idx_fc) == 0) or (len(idx_fm) == 0):
        # dummy magnetic to the electric multiplication operator
        K_op_c = _get_operator_zeros(idx_fc)

        # dummy electric to the magnetic multiplication operator
        K_op_m = _get_operator_zeros(idx_fm)

        return K_op_c, K_op_m

    # get the face voxel incidence matrix
    (A_fv_net_c, idx_fvc) = _get_face_voxel_matrix(n, idx_vc, idx_fc, A_net_c)
    (A_fv_net_m, idx_fvm) = _get_face_voxel_matrix(n, idx_vm, idx_fm, A_net_m)

    # get the coupling operator (voxel to voxel)
    (K_op_c_tmp, K_op_m_tmp) = matrix_multiply.get_operator_coupling(idx_fvc, idx_fvm, K_tsr, mult_type)

    # function describing the coupling from the magnetic to the electric faces
    def K_op_c(var_fm):
        var_fc = A_fv_net_c.transpose() * K_op_c_tmp(A_fv_net_m * var_fm)
        return var_fc

    # function describing the coupling from the electric to the magnetic faces
    def K_op_m(var_fc):
        var_fm = A_fv_net_m.transpose() * K_op_m_tmp(A_fv_net_c * var_fc)
        return var_fm

    return K_op_c, K_op_m
