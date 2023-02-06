"""
Different functions for building the equation system.
Two equation systems are built, one for the preconditioner and one for the full system.

The voxel structure has the following size: (nx, ny, nz).
The problem contains n_v non-empty voxels and n_f internal faces.
The problem contains n_src_c current source voxels and n_src_v voltage source voxels.

The equations are set in the following order:
    - n_f: equations are the KVL
    - n_v: equations are the KCL
    - n_src_c equations are the current source voxels (source equation with internal admittance)
    - n_src_v equations are the voltage source voxels (source equation with internal resistance)

The complete equation matrix is:
    [
        Z, A_kvl ;
        A_kcl, A_src ;
    ]

The complete solution vector is:
    [
        n_f: face currents
        n_v: voxel potentials
        n_src_c: current source currents
        n_src_v: voltage source currents
    ]

The complete right-hand size vector is:
    [
        n_f: zero excitation
        n_v: zero excitation
        n_src_c: current source excitations
        n_src_v: voltage source excitations
    ]

For the preconditioner, the impedance matrix (Z) is diagonal.
The preconditioner is solved with the Schur complement and the matrix factorization.

For the full system, the impedance matrix (Z) is dense.
The matrix-vector multiplication is done with FFT circulant tensors.
The system is meant to be solved with an iterative solver.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np
import scipy.sparse as sps
import scipy.sparse.linalg as sla
from PyPEEC.lib_matrix import matrix_factorization
from PyPEEC.lib_matrix import matrix_multiply


def _get_cond_fact(A_kvl, A_kcl, A_kcl_src, A_src_pot, A_src_src, R_vec, ZL_vec):
    """
    Compute the sparse matrix decomposition for the preconditioner.
    The preconditioner is using a diagonal impedance matrix (no cross-coupling).
    The diagonal impedance matrix can be trivially inverted.
    Therefore, the factorization is computed on the Schur complement:
        - with matrix factorization (UMFPACK solver)
        - with LU decomposition (SuperLU solver)

    The diagonal admittance matrix has the following size: (n_f, n_f).
    The Schur complement matrix has the following size: (n_v+n_src_c+n_src_v, n_v+n_src_c+n_src_v).
    """

    # get the system size
    (n_v, n_f) = A_kcl.shape
    (n_src, n_src) = A_src_src.shape

    # admittance vector
    Y_vec = 1 / (R_vec + ZL_vec)

    # admittance matrix
    Y_mat = sps.diags(Y_vec)

    # assemble the matrices around the diagonal matrix
    A_add = sps.csc_matrix((n_f, n_src), dtype=np.int64)
    A_12_mat = sps.bmat([[A_kvl, A_add]], dtype=np.int64)

    # assemble the matrices around the diagonal matrix
    A_add = sps.csc_matrix((n_src, n_f), dtype=np.int64)
    A_21_mat = sps.bmat([[A_kcl], [A_add]], dtype=np.int64)

    # assemble the matrices around the diagonal matrix
    A_add = sps.csc_matrix((n_v, n_v), dtype=np.int64)
    A_22_mat = sps.bmat([[A_add, A_kcl_src], [A_src_pot, A_src_src]], dtype=np.int64)

    # computing the Schur complement (with respect to the diagonal admittance matrix)
    S_mat = A_22_mat - A_21_mat * Y_mat * A_12_mat

    # compute the factorization of the sparse Schur complement
    _S_fact = matrix_factorization.MatrixFactorization(S_mat)

    return Y_mat, S_mat, _S_fact, A_12_mat, A_21_mat


def _get_cond_solve(rhs, Y_mat, _S_fact, A_12_mat, A_21_mat):
    """
    Solve the preconditioner equation system.
    The Schur complement and matrix factorization are used.

    The equation system has the following size: n_f+n_v+n_src_c+n_src_v.
    The Schur complement split the system in two subsystems: n_f and n_v+n_src_c+n_src_v.
    """

    # split the excitation vector (Schur complement split)
    (n_schur, n_schur) = Y_mat.shape

    rhs_a = rhs[:n_schur]
    rhs_b = rhs[n_schur:]

    # solve the equation system (Schur complement and matrix factorization)
    tmp = rhs_b-(A_21_mat*(Y_mat*rhs_a))
    sol_b = _S_fact.get_solution(tmp)
    sol_a = Y_mat*(rhs_a-(A_12_mat*sol_b))

    # assemble the solution
    sol = np.concatenate((sol_a, sol_b))

    return sol


def _get_system_multiply(sol, idx_f, A_kvl, A_kcl, A_kcl_src, A_src_pot, A_src_src, R_vec, ZL_tsr):
    """
    Multiply the full equation matrix with a given solution test vector.
    For the multiplication of inductance matrix and the current, the FFT circulant tensor is used.

    The equation system has the following size: n_f+n_v+n_src_c+n_src_v.
    """

    # get the system size
    (n_v, n_f) = A_kcl.shape
    (n_src, n_src) = A_src_src.shape

    # split the excitation vector
    sol_f = sol[0:n_f]
    sol_v = sol[n_f:n_f+n_v]
    sol_src = sol[n_f+n_v:n_f+n_v+n_src]

    # multiply the impedance matrix with the current vector (done with the FFT circulant tensor)
    rhs_f_tmp = matrix_multiply.get_multiply_diag(idx_f, sol_f, ZL_tsr)

    # form the complete KVL
    rhs_f = rhs_f_tmp+R_vec*sol_f+A_kvl*sol_v

    # form the complete KCL
    rhs_v = A_kcl*sol_f+A_kcl_src*sol_src

    # form the source equation
    rhs_src = A_src_pot*sol_v+A_src_src*sol_src

    # assemble the solution
    rhs = np.concatenate((rhs_f, rhs_v, rhs_src))

    return rhs


def _get_matrix_size(idx_v, idx_f, idx_src_c, idx_src_v):
    """
    Get the equation system size (Schur complement and total size).
    """

    # get the matrix size (for the Schur complement)
    n_a = len(idx_f)
    n_b = len(idx_v)+len(idx_src_c)+len(idx_src_v)

    # get the total size
    n_dof = n_a+n_b

    return n_dof, n_a, n_b


def get_impedance_matrix(freq, idx_f, L_tsr, L_vec):
    """
    Transform the circulant inductance tensor into a FFT circulant impedance tensor.

    For solving the full system, circulant tensors are used: (2*nx, 2*ny, 2*nz, 3).
    For solving the preconditioner, vectors are used: n_f.
    """

    # get the angular frequency
    s = 1j*2*np.pi*freq

    # compute the FFT circulant tensor (in order to make matrix-vector multiplication with FFT)
    L_tsr = matrix_multiply.get_prepare_diag(idx_f, L_tsr)

    # compute the impedance
    ZL_tsr = s*L_tsr

    # self-impedance for the preconditioner
    ZL_vec = s*L_vec

    return ZL_tsr, ZL_vec


def get_source_vector(idx_vc, idx_vm, idx_fc, idx_fm, I_src_c, V_src_v):
    """
    Construct the right-hand side with the current and voltage sources.

    The right-hand size vector has the following size: n_f+n_v+n_src_c+n_src_v.
    """

    # extract the voxel data
    n_v = len(idx_vc)+len(idx_vm)
    n_f = len(idx_fc)+len(idx_fm)

    # excitation are handled separately
    rhs_zero = np.zeros(n_v+n_f, dtype=np.complex128)

    # assemble
    rhs = np.concatenate((rhs_zero, I_src_c, V_src_v))

    return rhs


def get_kvl_kcl_matrix(A_reduced):
    """
    Construct the connection matrices for the KCL, KVL.

    The A_kvl matrix has the following size: (n_f, n_v+n_src_c+n_src_v).
    The A_kcl matrix has the following size: (n_v+n_src_c+n_src_v, n_f).
    """

    # connection matrix for the KCL
    A_kcl = +1*A_reduced

    # connection matrix for the KVL
    A_kvl = -1*A_reduced.transpose()

    return A_kvl, A_kcl


def get_source_matrix(idx_v, idx_src_c, idx_src_v, G_src_c, R_src_v):
    """
    Construct the source matrix (description of the sources with internal resistances/admittances).

    The A_src matrix has the following size: (n_v+n_src_c+n_src_v, n_v+n_src_c+n_src_v).
    """

    # extract the voxel data
    n_v = len(idx_v)
    n_src_c = len(idx_src_c)
    n_src_v = len(idx_src_v)

    # get the local source indices
    idx_src_c_local = np.flatnonzero(np.in1d(idx_v, idx_src_c))
    idx_src_v_local = np.flatnonzero(np.in1d(idx_v, idx_src_v))

    # indices of the new source equations to be added
    idx_src_c_add = np.arange(0, n_src_c, dtype=np.int64)
    idx_src_v_add = np.arange(n_src_c, n_src_c+n_src_v, dtype=np.int64)

    # constant vector with the size of the sources
    cst_src_c = np.full(n_src_c, 1, dtype=np.float64)
    cst_src_v = np.full(n_src_v, 1, dtype=np.float64)

    # matrix between the KCL equations and the source variables
    idx_row = np.concatenate((idx_src_c_local, idx_src_v_local))
    idx_col = np.concatenate((idx_src_c_add, idx_src_v_add))
    val = np.concatenate((-cst_src_c, -cst_src_v))
    A_kcl_src = sps.csc_matrix((val, (idx_row, idx_col)), shape=(n_v, n_src_c+n_src_v), dtype=np.float64)

    # matrix between the source equations and the potential variables
    idx_row = np.concatenate((idx_src_v_add, idx_src_c_add))
    idx_col = np.concatenate((idx_src_v_local, idx_src_c_local))
    val = np.concatenate((cst_src_v, G_src_c))
    A_src_pot = sps.csc_matrix((val, (idx_row, idx_col)), shape=(n_src_c+n_src_v, n_v), dtype=np.float64)

    # matrix between the source equations and the source variables
    idx_row = np.concatenate((idx_src_c_add, idx_src_v_add))
    idx_col = np.concatenate((idx_src_c_add, idx_src_v_add))
    val = np.concatenate((cst_src_c, R_src_v))
    A_src_src = sps.csc_matrix((val, (idx_row, idx_col)), shape=(n_src_c+n_src_v, n_src_c+n_src_v), dtype=np.float64)

    return A_kcl_src, A_src_pot, A_src_src


def get_cond_operator(A_kvl, A_kcl, A_kcl_src, A_src_pot, A_src_src, R_vec, ZL_vec):
    """
    Get a linear operator that solves the preconditioner equation system.
    This operator is used as a preconditioner for the iterative method solving the full system.
    """

    # get the system size
    (n_v, n_f) = A_kcl.shape
    (n_src, n_src) = A_src_src.shape

    # get system size
    n_dof = n_v + n_f + n_src

    # get the Schur complemement
    (Y_mat, S_mat, _S_fact, A_12_mat, A_21_mat) = _get_cond_fact(A_kvl, A_kcl, A_kcl_src, A_src_pot, A_src_src, R_vec, ZL_vec)

    # if the matrix is singular, there is not preconditioner
    if not _S_fact.get_status():
        return None

    # function describing the preconditioner
    def fct(rhs):
        sol = _get_cond_solve(rhs, Y_mat, _S_fact, A_12_mat, A_21_mat)
        return sol

    # corresponding linear operator
    op = sla.LinearOperator((n_dof, n_dof), matvec=fct)

    return op, S_mat


def get_system_operator(idx_f, A_kvl, A_kcl, A_kcl_src, A_src_pot, A_src_src, R_vec, ZL_tsr):
    """
    Get a linear operator that produce the matrix-vector multiplication result for the full system.
    This operator is used for the iterative solver.
    """

    # get the system size
    (n_v, n_f) = A_kcl.shape
    (n_src, n_src) = A_src_src.shape

    # get system size
    n_dof = n_v + n_f + n_src

    # function describing the equation system
    def fct(sol):
        rhs = _get_system_multiply(sol, idx_f, A_kvl, A_kcl, A_kcl_src, A_src_pot, A_src_src, R_vec, ZL_tsr)
        return rhs

    # corresponding linear operator
    op = sla.LinearOperator((n_dof, n_dof), matvec=fct)

    return op
