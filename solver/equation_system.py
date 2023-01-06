"""
Different functions for building the equation system.
Two equation systems are built, one for the preconditioner and one for the full system.

The complete equation matrix is: [Z A_kvl ; A_kcl A_src].
The complete solution vector is [face_currents ; voxel_potentials ; voltage_source_currents].
The complete right-hand size vector is [zero_excitation ; current_source_currents ; voltage_source_voltages].

The problem contains n_v non-empty voxels and n_f internal faces.
The problem contains n_src_v voltage source voxels.

The equations are set in the following order:
    - n_f: equations are the KVL
    - n_v: equations are the KCL
    - n_src_v equations are the voltage source voxels (potential fixing)

The solution vector is set in the following order:
    - n_f: face currents
    - n_v: voxel potentials
    - n_src_v: voltage source currents

The right-hand side vector is set in the following order:
    - n_f: zero excitation
    - n_v: current source excitations
    - n_src_v: voltage source excitations

For the preconditioner, the impedance matrix (Z) is diagonal.
The preconditioner is solved with the Schur complement and the LU decomposition.

For the full system, the impedance matrix (Z) is dense.
The matrix-vector multiplication is done with FFT circulant tensors.
The system is solved with an iterative solver.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np
import scipy.fft as fft
import scipy.sparse as sps
import scipy.sparse.linalg as sla


def __get_circulant_multiply(CF, X):
    """
    Matrix-vector multiplication with FFT.
    The matrix is shaped as a FFT circulant tensor.
    The vector is also shaped as a tensor.
    The size of the FFT circulant tensor is twice the size of the vector.
    The size of result is the same as the size of the vector.
    """

    # extract the input tensor data
    (nx, ny, nz) = X.shape
    (nnx, nny, nnz) = CF.shape

    # compute the FFT of the vector (result is the same size as the FFT circulant tensor)
    CX = fft.fftn(X, (nnx, nny, nnz))

    # matrix vector multiplication in frequency domain with the FFT circulant tensor
    CY = CF*CX

    # compute the iFFT
    Y = fft.ifftn(CY)

    # the result is in the first block of the matrix
    Y = Y[0:nx, 0:ny, 0:nz]

    return Y


def __get_preconditioner_decomposition(A_kcl, A_kvl, A_src, R_vector, ZL_vector):
    """
    Compute the sparse LU decomposition for the preconditioner.
    The preconditioner is using a diagonal impedance matrix (no cross-coupling).
    The diagonal impedance matrix can be trivially inverted.
    Therefore, the LU decomposition is computed on the Schur complement.

    The problem contains n_v non-empty voxels and n_f internal faces.
    The problem contains n_src_v voltage source voxels.
    The diagonal admittance matrix as the following size: (n_f, n_f).
    The Schur complement matrix as the following size: (n_v+n_src_v, n_v+n_src_v).
    """

    # admittance vector
    Y_vector = 1/(R_vector+ZL_vector)

    # admittance matrix
    Y_matrix = sps.diags(Y_vector)

    # computing the Schur complement (with respect to the diagonal admittance matrix)
    S_matrix = A_src-A_kcl*Y_matrix*A_kvl

    # compute the LU decomposition of the sparse Schur complement (None if singular)
    try:
        LU_decomposition = sla.splu(S_matrix)
    except RuntimeError:
        LU_decomposition = None

    return Y_matrix, LU_decomposition


def __get_preconditioner_solve(rhs, idx_v, idx_f, idx_src_v_local, A_kcl, A_kvl, Y_matrix, LU_decomposition):
    """
    Solve the preconditioner equation system.
    The Schur complement and LU decomposition are used.

    The problem contains n_v non-empty voxels and n_f internal faces.
    The problem contains n_src_v voltage source voxels.
    The equation system has the following size: n_f+n_v+n_src_v.
    The Schur complement split the system in two subsystems: n_f and n_v+n_src_v.
    """

    # get the matrix size (Schur complement split)
    n_a = len(idx_f)
    n_b = len(idx_v)+len(idx_src_v_local)

    # split the excitation vector (Schur complement split)
    rhs_a = rhs[0:n_a]
    rhs_b = rhs[n_a:n_a+n_b]

    # solve the equation system (Schur complement and LU decomposition)
    tmp = rhs_b-(A_kcl*(Y_matrix*rhs_a))
    sol_b = LU_decomposition.solve(tmp)
    sol_a = Y_matrix*(rhs_a-(A_kvl*sol_b))

    # assemble the solution
    sol = np.concatenate((sol_a, sol_b), dtype=np.complex128)

    return sol


def __get_system_multiply(sol, n, idx_v, idx_f, idx_src_v_local, A_kcl, A_kvl, A_src, R_tensor, ZL_tensor):
    """
    Multiply the full equation matrix with a given solution test vector.
    For the multiplication of resistance matrix and the current, the Hadamard product is used.
    For the multiplication of inductance matrix and the current, the FFT circulant tensor is used.

    The problem contains n_v non-empty voxels and n_f internal faces.
    The problem contains n_src_v voltage source voxels.
    The equation system has the following size: n_f+n_v+n_src_v.
    """

    # get the matrix size
    n_a = len(idx_f)
    n_b = len(idx_v)+len(idx_src_v_local)
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

    # initialize the tensor for the matrix multiplication results
    rhs_a_all = np.zeros((nx, ny, nz, 3), dtype=np.complex128)

    # multiply the impedance matrix with the current vector
    for i in range(3):
        # for the inductive component, the multiplication is done with the FFT circulant tensor
        rhs_a_all[:, :, :, i] += __get_circulant_multiply(ZL_tensor[:, :, :, i], sol_a_all[:, :, :, i])

        # for the resistive component, the multiplication is done with the Hadamard product
        rhs_a_all[:, :, :, i] += R_tensor[:, :, :, i]*sol_a_all[:, :, :, i]

    # flatten the tensor into a vector
    rhs_a_all = rhs_a_all.flatten(order="F")

    # form the complete KVL
    rhs_a = rhs_a_all[idx_f]+A_kvl*sol_b

    # form the complete KCL and potential fixing
    rhs_b = A_kcl*sol_a+A_src*sol_b

    # assemble the solution
    rhs = np.concatenate((rhs_a, rhs_b), dtype=np.complex128)

    return rhs


def get_source_vector(idx_v, idx_f, idx_src_c_local, val_src_c, val_src_v):
    """
    Construct the right-hand side with the current and voltage sources.

    The problem contains n_v non-empty voxels and n_f internal faces.
    The problem contains n_src_v voltage source voxels.
    The right-hand size vector has the following size: n_f+n_v+n_src_v.
    """

    # extract the voxel data
    n_v = len(idx_v)
    n_f = len(idx_f)

    # no excitation for the KVL
    rhs_zero = np.zeros(n_f, dtype=np.complex128)

    # current sources are connected to the KCL
    rhs_current = np.zeros(n_v, dtype=np.complex128)
    rhs_current[idx_src_c_local] = val_src_c

    # voltage sources are separate equations
    rhs_voltage = val_src_v

    # assemble
    rhs = np.concatenate((rhs_zero, rhs_current, rhs_voltage), dtype=np.complex128)

    return rhs


def get_connection_matrix(A_reduced, idx_v, idx_f, idx_src_v_local):
    """
    Construct the connection matrices for the KCL, KVL, and potential fixing.

    The problem contains n_v non-empty voxels and n_f internal faces.
    The problem contains n_src_v voltage source voxels.
    The A_kcl matrix has the following size: (n_v+n_src_v, n_f).
    The A_kvl matrix has the following size: (n_f, n_v+n_src_v).
    The A_src matrix has the following size: (n_v+n_src_v, n_v+n_src_v).
    """

    # extract the voxel data
    n_v = len(idx_v)
    n_f = len(idx_f)
    n_src_v = len(idx_src_v_local)

    # connection matrix for the KCL
    A_add = sps.csc_matrix((n_src_v, n_f), dtype=np.int64)
    A_kcl = sps.bmat([[+1*A_reduced], [A_add]], dtype=np.int64)

    # connection matrix for the KVL
    A_add = sps.csc_matrix((n_f, n_src_v), dtype=np.int64)
    A_kvl = sps.bmat([[-1*A_reduced.transpose(), A_add]], dtype=np.int64)

    # connection matrix for the source (one equation per voltage source voxel)
    # the -1 term represents the current flowing inside/outside the voltage source voxels
    # the +1 term represents the potential fixing for the voltage source voxels
    idx_add = np.arange(n_v, n_v+n_src_v, dtype=np.int64)
    idx_row = np.concatenate((idx_src_v_local, idx_add), dtype=np.int64)
    idx_col = np.concatenate((idx_add, idx_src_v_local), dtype=np.int64)
    data = np.concatenate((np.full(n_src_v, -1), np.full(n_src_v, +1)), dtype=np.int64)
    A_src = sps.csc_matrix((data, (idx_row, idx_col)), shape=(n_v+n_src_v, n_v+n_src_v), dtype=np.int64)

    return A_kcl, A_kvl, A_src


def get_preconditioner_operator(idx_v, idx_f, idx_src_v_local, A_kcl, A_kvl, A_src, R_vector, ZL_vector):
    """
    Get a linear operator that solves the preconditioner equation system.
    This operator is used as a preconditioner for the iterative method solving the full system.
    """

    # get the matrix size
    n_dof = len(idx_f)+len(idx_v)+len(idx_src_v_local)

    # LU decomposition with the Schur complement
    (Y_matrix, LU_decomposition) = __get_preconditioner_decomposition(A_kcl, A_kvl, A_src, R_vector, ZL_vector)

    # if the matrix is singular, there is not preconditioner
    if LU_decomposition is None:
        return None

    # function describing the preconditioner
    def fct(rhs):
        sol = __get_preconditioner_solve(rhs, idx_v, idx_f, idx_src_v_local, A_kcl, A_kvl, Y_matrix, LU_decomposition)
        return sol

    # corresponding linear operator
    op = sla.LinearOperator((n_dof, n_dof), matvec=fct)

    return op


def get_system_operator(n, idx_v, idx_f, idx_src_v_local, A_kcl, A_kvl, A_src, R_tensor, ZL_tensor):
    """
    Get a linear operator that produce the matrix-vector multiplication result for the full system.
    This operator is used for the iterative solver.
    """

    # get the matrix size
    n_dof = len(idx_f)+len(idx_v)+len(idx_src_v_local)

    # function describing the equation system
    def fct(sol):
        rhs = __get_system_multiply(sol, n, idx_v, idx_f, idx_src_v_local, A_kcl, A_kvl, A_src, R_tensor, ZL_tensor)
        return rhs

    # corresponding linear operator
    op = sla.LinearOperator((n_dof, n_dof), matvec=fct)

    return op


def get_singular(A_kcl, A_kvl, A_src):
    """
    Computing the Schur complement with an identity impedance matrix.
    The resulting matrix is used to detect quasi-singular equations systems.

    An identity impedance matrix is used for two reasons:
        - the resulting matrix only contains integers
        - the resulting condition number is only dependent on the interconnection between the voxels

    It should be noted that the resulting matrix has no physical meaning.
    """

    # computing the Schur complement (using an identity impedance matrix)
    S_matrix = A_src-A_kcl*A_kvl

    return S_matrix