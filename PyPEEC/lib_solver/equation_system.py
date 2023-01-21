"""
Different functions for building the equation system.
Two equation systems are built, one for the preconditioner and one for the full system.

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
from PyPEEC.lib_matrix import fourier_transform


def _get_circulant_multiply(nx, ny, nz, CF, X):
    """
    Matrix-vector multiplication with FFT.
    The matrix is shaped as a FFT circulant tensor.
    The vector is also shaped as a tensor.
    The size of the FFT circulant tensor is twice the size of the vector.
    The size of result is the same as the size of the vector.
    """

    # compute the FFT of the vector (result is the same size as the FFT circulant tensor)
    CX = fourier_transform.get_fft_tensor(X, True)

    # matrix vector multiplication in frequency domain with the FFT circulant tensor
    CY = CF*CX

    # compute the iFFT
    Y = fourier_transform.get_ifft_tensor(CY, False)

    # the result is in the first block of the matrix
    Y = Y[0:nx, 0:ny, 0:nz, :]

    return Y


def _get_preconditioner_factorization(A_kvl, A_kcl, A_src, R_vector, ZL_vector):
    """
    Compute the sparse matrix decomposition for the preconditioner.
    The preconditioner is using a diagonal impedance matrix (no cross-coupling).
    The diagonal impedance matrix can be trivially inverted.
    Therefore, the factorization is computed on the Schur complement:
        - with sparse matrix solver (UMFPACK solver)
        - with LU decomposition (SuperLU solver)
        - SuperLU is used if UMFPACK is not installed

    The problem contains n_v non-empty voxels and n_f internal faces.
    The problem contains n_src_c current source voxels and n_src_v voltage source voxels.
    The diagonal admittance matrix as the following size: (n_f, n_f).
    The Schur complement matrix as the following size: (n_v+n_src_c+n_src_v, n_v+n_src_c+n_src_v).
    """

    # admittance vector
    Y_vector = 1/(R_vector+ZL_vector)

    # admittance matrix
    Y_matrix = sps.diags(Y_vector)

    # computing the Schur complement (with respect to the diagonal admittance matrix)
    S_matrix = A_src-A_kcl*Y_matrix*A_kvl

    # compute the factorization of the sparse Schur complement
    S_factorization = matrix_factorization.MatrixFactorization(S_matrix)

    return Y_matrix, S_factorization


def _get_preconditioner_solve(rhs, n_a, n_b, A_kvl, A_kcl, Y_matrix, S_factorization):
    """
    Solve the preconditioner equation system.
    The Schur complement and matrix factorization are used.

    The problem contains n_v non-empty voxels and n_f internal faces.
    The problem contains n_src_c current source voxels and n_src_v voltage source voxels.
    The equation system has the following size: n_f+n_v+n_src_c+n_src_v.
    The Schur complement split the system in two subsystems: n_f and n_v+n_src_c+n_src_v.
    """

    # split the excitation vector (Schur complement split)
    rhs_a = rhs[0:n_a]
    rhs_b = rhs[n_a:n_a+n_b]

    # solve the equation system (Schur complement and matrix factorization)
    tmp = rhs_b-(A_kcl*(Y_matrix*rhs_a))
    sol_b = S_factorization.get_solution(tmp)
    sol_a = Y_matrix*(rhs_a-(A_kvl*sol_b))

    # assemble the solution
    sol = np.concatenate((sol_a, sol_b), dtype=np.complex128)

    return sol


def _get_system_multiply(sol, n, n_a, n_b, idx_f, A_kvl, A_kcl, A_src, R_vector, ZL_tensor):
    """
    Multiply the full equation matrix with a given solution test vector.
    For the multiplication of inductance matrix and the current, the FFT circulant tensor is used.

    The problem contains n_v non-empty voxels and n_f internal faces.
    The problem contains n_src_c current source voxels and n_src_v voltage source voxels.
    The equation system has the following size: n_f+n_v+n_src_c+n_src_v.
    """

    # get the matrix size
    (nx, ny, nz) = n
    n = nx*ny*nz

    # split the excitation vector
    sol_a = sol[0:n_a]
    sol_b = sol[n_a:n_a+n_b]

    # expand the current excitation into a vector with all the faces
    sol_a_all = np.zeros(3*n, dtype=np.complex128)
    sol_a_all[idx_f] = sol_a

    # reshape the current excitation into a tensor
    sol_a_all = sol_a_all.reshape((nx, ny, nz, 3), order="F")

    # multiply the impedance matrix with the current vector (multiplication is done with the FFT circulant tensor)
    rhs_a_all = _get_circulant_multiply(nx, ny, nz, ZL_tensor, sol_a_all)

    # flatten the tensor into a vector
    rhs_a_all = rhs_a_all.flatten(order="F")

    # form the complete KVL
    rhs_a = rhs_a_all[idx_f]+R_vector*sol_a+A_kvl*sol_b

    # form the complete KCL and potential fixing
    rhs_b = A_kcl*sol_a+A_src*sol_b

    # assemble the solution
    rhs = np.concatenate((rhs_a, rhs_b), dtype=np.complex128)

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


def get_impedance_matrix(freq, L_tensor, L_vector):
    """
    Transform the circulant inductance tensor into a FFT circulant impedance tensor.
    The problem contains n_f internal faces.
    For solving the full system, circulant tensors are used: (2*nx, 2*ny, 2*nz, 3).
    For solving the preconditioner, vectors are used: (n_f).
    """

    # get the angular frequency
    s = 1j*2*np.pi*freq

    # compute the FFT and the impedance
    ZL_tensor = fourier_transform.get_fft_tensor(L_tensor, False)
    ZL_tensor = s*ZL_tensor

    # self-impedance for the preconditioner
    ZL_vector = s*L_vector

    return ZL_tensor, ZL_vector


def get_source_vector(idx_v, idx_f, I_src_c, V_src_v):
    """
    Construct the right-hand side with the current and voltage sources.

    The problem contains n_v non-empty voxels and n_f internal faces.
    The problem contains n_src_c current source voxels and n_src_v voltage source voxels.
    The right-hand size vector has the following size: n_f+n_v+n_src_c+n_src_v.
    """

    # extract the voxel data
    n_v = len(idx_v)
    n_f = len(idx_f)

    # no excitation for the KVL
    rhs_zero = np.zeros(n_f, dtype=np.complex128)

    # current sources are connected to the KCL
    rhs_current = np.zeros(n_v, dtype=np.complex128)

    # assemble
    rhs = np.concatenate((rhs_zero, rhs_current, I_src_c, V_src_v), dtype=np.complex128)

    return rhs


def get_kvl_kcl_matrix(A_reduced, idx_f, idx_src_c, idx_src_v):
    """
    Construct the connection matrices for the KCL, KVL.

    The problem contains n_v non-empty voxels and n_f internal faces.
    The problem contains n_src_c current source voxels and n_src_v voltage source voxels.
    The A_kvl matrix has the following size: (n_f, n_v+n_src_c+n_src_v).
    The A_kcl matrix has the following size: (n_v+n_src_c+n_src_v, n_f).
    """

    # extract the voxel data
    n_f = len(idx_f)
    n_src_c = len(idx_src_c)
    n_src_v = len(idx_src_v)

    # connection matrix for the KCL
    A_add = sps.csc_matrix((n_src_c+n_src_v, n_f), dtype=np.int64)
    A_kcl = sps.bmat([[+1*A_reduced], [A_add]], dtype=np.int64)

    # connection matrix for the KVL
    A_add = sps.csc_matrix((n_f, n_src_c+n_src_v), dtype=np.int64)
    A_kvl = sps.bmat([[-1*A_reduced.transpose(), A_add]], dtype=np.int64)

    return A_kvl, A_kcl


def get_source_matrix(idx_v, idx_src_c, idx_src_v, G_src_c, R_src_v):
    """
    Construct the source matrix (description of the sources with internal resistances/admittances).

    The problem contains n_v non-empty voxels.
    The problem contains n_src_c current source voxels and n_src_v voltage source voxels.
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
    idx_src_c_add = np.arange(n_v, n_v+n_src_c, dtype=np.int64)
    idx_src_v_add = np.arange(n_v+n_src_c, n_v+n_src_c+n_src_v, dtype=np.int64)

    # constant vector with the size of the sources
    cst_src_c = np.full(n_src_c, 1, dtype=np.float64)
    cst_src_v = np.full(n_src_v, 1, dtype=np.float64)

    # connection of the current source currents and voltage source currents to the KCL
    idx_row_connect = np.concatenate((idx_src_c_local, idx_src_v_local), dtype=np.int64)
    idx_col_connect = np.concatenate((idx_src_c_add, idx_src_v_add), dtype=np.int64)
    val_connect = np.concatenate((-cst_src_c, -cst_src_v), dtype=np.float64)

    # adding the current sources (source equation with internal admittance, Norton source)
    idx_row_current = np.concatenate((idx_src_c_add, idx_src_c_add), dtype=np.int64)
    idx_col_current = np.concatenate((idx_src_c_add, idx_src_c_local), dtype=np.int64)
    val_current = np.concatenate((cst_src_c, G_src_c), dtype=np.float64)

    # adding the voltage sources (source equation with internal resistance, Thevenin source)
    idx_row_voltage = np.concatenate((idx_src_v_add, idx_src_v_add), dtype=np.int64)
    idx_col_voltage = np.concatenate((idx_src_v_local, idx_src_v_add), dtype=np.int64)
    val_voltage = np.concatenate((cst_src_v, R_src_v), dtype=np.float64)

    # construct the matrix with the computed indices and values
    idx_row = np.concatenate((idx_row_connect, idx_row_current, idx_row_voltage), dtype=np.int64)
    idx_col = np.concatenate((idx_col_connect, idx_col_current, idx_col_voltage), dtype=np.int64)
    val = np.concatenate((val_connect, val_current, val_voltage), dtype=np.float64)
    A_src = sps.csc_matrix((val, (idx_row, idx_col)), shape=(n_v+n_src_c+n_src_v, n_v+n_src_c+n_src_v), dtype=np.float64)

    return A_src


def get_preconditioner_operator(idx_v, idx_f, idx_src_c, idx_src_v, A_kvl, A_kcl, A_src, R_vector, ZL_vector):
    """
    Get a linear operator that solves the preconditioner equation system.
    This operator is used as a preconditioner for the iterative method solving the full system.
    """

    # get the matrix size
    (n_dof, n_a, n_b) = _get_matrix_size(idx_v, idx_f, idx_src_c, idx_src_v)

    # matrix factorization with the Schur complement
    (Y_matrix, S_factorization) = _get_preconditioner_factorization(A_kvl, A_kcl, A_src, R_vector, ZL_vector)

    # if the matrix is singular, there is not preconditioner
    if not S_factorization.get_status():
        return None

    # function describing the preconditioner
    def fct(rhs):
        sol = _get_preconditioner_solve(rhs, n_a, n_b, A_kvl, A_kcl, Y_matrix, S_factorization)
        return sol

    # corresponding linear operator
    op = sla.LinearOperator((n_dof, n_dof), matvec=fct)

    return op


def get_system_operator(n, idx_v, idx_f, idx_src_c, idx_src_v, A_kvl, A_kcl, A_src, R_vector, ZL_tensor):
    """
    Get a linear operator that produce the matrix-vector multiplication result for the full system.
    This operator is used for the iterative solver.
    """

    # get the matrix size
    (n_dof, n_a, n_b) = _get_matrix_size(idx_v, idx_f, idx_src_c, idx_src_v)

    # function describing the equation system
    def fct(sol):
        rhs = _get_system_multiply(sol, n, n_a, n_b, idx_f, A_kvl, A_kcl, A_src, R_vector, ZL_tensor)
        return rhs

    # corresponding linear operator
    op = sla.LinearOperator((n_dof, n_dof), matvec=fct)

    return op


def get_singular(A_kvl, A_kcl, A_src, R_vector, ZL_vector):
    """
    Computing the Schur complement with the diagonal impedance matrix.
    The resulting matrix is used to detect quasi-singular equations systems.
    It should be noted that the resulting matrix has no physical meaning.
    """

    # admittance vector
    Y_vector = 1/(R_vector+ZL_vector)

    # admittance matrix
    Y_matrix = sps.diags(Y_vector)

    # computing the Schur complement
    S_matrix = A_src-A_kcl*Y_matrix*A_kvl

    return S_matrix
