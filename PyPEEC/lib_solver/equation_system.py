"""
Different functions for building the equation system.
Two equation systems are built, one for the preconditioner and one for the full system.

The voxel structure has the following size: (nx, ny, nz).
The problem contains n_vc non-empty electric voxels and n_vm non-empty magnetic voxels.
The problem contains n_fc internal electric faces and n_fm internal magnetic faces.
The problem contains n_src_c current source voxels and n_src_v voltage source voxels.

The equations are set in the following order:
    - n_fc: the electric KVL equations
    - n_fm: the magnetic KVL equations
    - n_vc: the electric KCL equations
    - n_vm: the magnetic KCL equations
    - n_src_c: the current source voxels equations (source equation with internal admittance)
    - n_src_v: the voltage source voxels equations (source equation with internal resistance)

The complete equation matrix is:
    [
        R_c+s*L_c,   K_c,            A_kvl_c,     0,          0 ;
        K_m,         R_m,            0,           A_kvl_m,    0 ;
        A_kcl_c,     0,              0,           0,          A_vc_src ;
        0,           P_m*A_kcl_m,    0,           s*I,        A_vm_src ;
        0,           0,              A_src_vc,    A_src_vm,   A_src_src ;
    ]

The complete solution vector is:
    [
        n_fc: electric face currents
        n_fm: magnetic face fluxes
        n_vc: electric voxel potentials
        n_vm: magnetic voxel potentials
        n_src_c: current source currents
        n_src_v: voltage source currents
    ]

The complete right-hand size vector is:
    [
        n_fc: zero excitation
        n_fm: zero excitation
        n_vc: zero excitation
        n_vm: zero excitation
        n_src_c: current source excitations
        n_src_v: voltage source excitations
    ]

For the DC problem (zero frequency), division per zero are occurring.
Therefore, the problem is formulated slightly differently for this case.

For the preconditioner, the diagonal of the inductance and potential matrix is used.
For the preconditioner, the electric-magnetic coupling matrices are neglected.
The preconditioner is solved with the Schur complement and the matrix factorization.

For the full system, the complete dense matrix are used.
The system is meant to be solved with an iterative solver.
Therefore, the full system matrix is not built and a matrix-vector operator is returned.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np
import scipy.sparse as sps
import scipy.sparse.linalg as sla
from PyPEEC.lib_matrix import matrix_factorization


def _get_split_sol(sol, A_c, A_m, A_src):
    # get the matrices
    (A_kvl_c, A_kcl_c) = A_c
    (A_kvl_m, A_kcl_m) = A_m
    (A_vc_src, A_src_vc, A_src_src) = A_src

    # get the system size
    (n_vc, n_fc) = A_kcl_c.shape
    (n_vm, n_fm) = A_kcl_m.shape
    (n_src, n_src) = A_src_src.shape

    sol_c = sol[0:n_fc+n_vc+n_src]
    sol_m = sol[n_fc+n_vc+n_src:n_fc+n_vc+n_src+n_fm+n_vm]

    return sol_c, sol_m


def _get_split_rhs(rhs, A_c, A_m, A_src):
    # get the matrices
    (A_kvl_c, A_kcl_c) = A_c
    (A_kvl_m, A_kcl_m) = A_m
    (A_vc_src, A_src_vc, A_src_src) = A_src

    # get the system size
    (n_vc, n_fc) = A_kcl_c.shape
    (n_vm, n_fm) = A_kcl_m.shape
    (n_src, n_src) = A_src_src.shape

    # split the rhs vector
    rhs_kvl_c = rhs[0:n_fc]
    rhs_kcl_c = rhs[n_fc:n_fc+n_vc]
    rhs_src = rhs[n_fc+n_vc:n_fc+n_vc+n_src]
    rhs_kvl_m = rhs[n_fc+n_vc+n_src:n_fc+n_vc+n_src+n_fm]
    rhs_kcl_m = rhs[n_fc+n_vc+n_src+n_fm:n_fc+n_vc+n_src+n_fm+n_vm]

    # assemble the vector
    rhs_c = np.concatenate((rhs_kvl_c, rhs_kcl_c, rhs_src))
    rhs_m = np.concatenate((rhs_kvl_m, rhs_kcl_m))

    return rhs_c, rhs_m


def _get_update_rhs(sol_c, sol_m, freq, A_c, A_m, A_src, K_op_c, K_op_m):
    # get the matrices
    (A_kvl_c, A_kcl_c) = A_c
    (A_kvl_m, A_kcl_m) = A_m
    (A_vc_src, A_src_vc, A_src_src) = A_src

    # get the system size
    (n_vc, n_fc) = A_kcl_c.shape
    (n_vm, n_fm) = A_kcl_m.shape
    (n_src, n_src) = A_src_src.shape

    # get the derivative operator (avoid singularity for DC solution)
    if freq == 0:
        k_c_fact = 0
        k_m_fact = 1
    else:
        k_c_fact = 1
        k_m_fact = 1

    # split the electric solution vector
    I_fc = sol_c[0:n_fc]
    I_fm = sol_m[0:n_fm]

    rhs_add_fc = k_c_fact*K_op_c(I_fm)
    rhs_add_vc = np.zeros(n_vc, dtype=np.complex128)
    rhs_add_src = np.zeros(n_src, dtype=np.complex128)
    rhs_add_c = np.concatenate((rhs_add_fc, rhs_add_vc, rhs_add_src))

    rhs_add_fm = k_m_fact*K_op_m(I_fc)
    rhs_add_vm = np.zeros(n_vm, dtype=np.complex128)
    rhs_add_m = np.concatenate((rhs_add_fm, rhs_add_vm))

    return rhs_add_c, rhs_add_m


def _get_assemble_sol(sol_c, sol_m, A_c, A_m, A_src):
    # get the matrices
    (A_kvl_c, A_kcl_c) = A_c
    (A_kvl_m, A_kcl_m) = A_m
    (A_vc_src, A_src_vc, A_src_src) = A_src

    # get the system size
    (n_vc, n_fc) = A_kcl_c.shape
    (n_vm, n_fm) = A_kcl_m.shape
    (n_src, n_src) = A_src_src.shape

    # assemble the vector
    sol = np.concatenate((sol_c, sol_m))

    return sol


def _get_cond_fact_electric(freq, A_c, R_vec_c, L_vec_c, A_src):
    """
    Compute the sparse matrices using for the preconditioner.

    For the preconditioner, the diagonal of the inductance and potential matrix is used.
    For the preconditioner, the electric-magnetic coupling matrices are neglected.

    The preconditioner matrix has the following form:
        [
            Z_mat,       A_12_mat;
            A_21_mat,    A_22_mat;
        ]

    The matrix impedance matrix (Z_mat) is diagonal.
    Therefore, the factorization is computed on the Schur complement.
    The Schur complement is computed as:
        - Y_mat = 1/Z_mat
        - S_mat = A_22_mat-A_21_mat*Y_mat*A_12_mat

    Two different methods are used to invert the Schur complement (S_mat):
        - with matrix factorization (UMFPACK solver)
        - with LU decomposition (SuperLU solver)

    The equation system has the following size: n_fc+n_fm+n_vc+n_vm+n_src_c+n_src_v.
    The Schur complement split the system in two subsystems:
        - n_fc+n_fm (diagonal block)
        - n_vc+n_vm+n_src_c+n_src_v
    """

    # get the matrices
    (A_kvl_c, A_kcl_c) = A_c
    (A_vc_src, A_src_vc, A_src_src) = A_src

    # get the system size
    (n_vc, n_fc) = A_kcl_c.shape
    (n_src, n_src) = A_src_src.shape

    # get the angular frequency
    s = 1j*2*np.pi*freq

    # get the electric admittance
    Y_vec_c = 1/(R_vec_c+s*L_vec_c)

    # admittance matrix
    Y_mat = sps.diags(Y_vec_c)

    # assemble the matrices
    A_12_mat = A_kvl_c
    A_21_mat = A_kcl_c
    A_22_mat = sps.csc_matrix((n_vc, n_vc), dtype=np.int64)

    # expand for the source matrices
    A_add = sps.csc_matrix((n_fc, n_src), dtype=np.int64)
    A_12_mat = sps.hstack([A_12_mat, A_add], dtype=np.complex128)
    A_add = sps.csc_matrix((n_src, n_fc), dtype=np.int64)
    A_21_mat = sps.vstack([A_21_mat, A_add], dtype=np.complex128)

    # add the source
    A_22_mat = sps.bmat([[A_22_mat, A_vc_src], [A_src_vc, A_src_src]], dtype=np.complex128)

    # computing the Schur complement (with respect to the diagonal admittance matrix)
    S_mat = A_22_mat-A_21_mat*Y_mat*A_12_mat

    # compute the factorization of the sparse Schur complement
    S_fact = matrix_factorization.MatrixFactorization(S_mat)

    return Y_mat, S_mat, S_fact, A_12_mat, A_21_mat


def _get_cond_fact_magnetic(freq, A_m, R_vec_m, P_vec_m):
    """
    Compute the sparse matrices using for the preconditioner.

    For the preconditioner, the diagonal of the inductance and potential matrix is used.
    For the preconditioner, the electric-magnetic coupling matrices are neglected.

    The preconditioner matrix has the following form:
        [
            Z_mat,       A_12_mat;
            A_21_mat,    A_22_mat;
        ]

    The matrix impedance matrix (Z_mat) is diagonal.
    Therefore, the factorization is computed on the Schur complement.
    The Schur complement is computed as:
        - Y_mat = 1/Z_mat
        - S_mat = A_22_mat-A_21_mat*Y_mat*A_12_mat

    Two different methods are used to invert the Schur complement (S_mat):
        - with matrix factorization (UMFPACK solver)
        - with LU decomposition (SuperLU solver)

    The equation system has the following size: n_fc+n_fm+n_vc+n_vm+n_src_c+n_src_v.
    The Schur complement split the system in two subsystems:
        - n_fc+n_fm (diagonal block)
        - n_vc+n_vm+n_src_c+n_src_v
    """

    # get the matrices
    (A_kvl_m, A_kcl_m) = A_m

    # get the system size
    (n_vm, n_fm) = A_kcl_m.shape

    # get the angular frequency
    s = 1j*2*np.pi*freq

    # get the magnetic admittance (avoid singularity for DC solution)
    if freq == 0:
        Y_vec_m = 1/R_vec_m
        I_vec_m = np.ones(n_vm, dtype=np.complex128)
    else:
        Y_vec_m = s/R_vec_m
        I_vec_m = s*np.ones(n_vm, dtype=np.complex128)

    # admittance matrix
    Y_mat = sps.diags(Y_vec_m)

    # potential matrix
    P_vec_m = P_vec_m
    P_mat_m = sps.diags(P_vec_m)
    I_mat_m = sps.diags(I_vec_m)

    # assemble the matrices
    A_12_mat = A_kvl_m
    A_21_mat = P_mat_m*A_kcl_m
    A_22_mat = I_mat_m

    # computing the Schur complement (with respect to the diagonal admittance matrix)
    S_mat = A_22_mat-A_21_mat*Y_mat*A_12_mat

    # compute the factorization of the sparse Schur complement
    S_fact = matrix_factorization.MatrixFactorization(S_mat)

    return Y_mat, S_mat, S_fact, A_12_mat, A_21_mat


def _get_cond_solve(rhs, Y_mat, _S_fact, A_12_mat, A_21_mat):
    """
    Solve the preconditioner equation system.
    The matrix factorization of the Schur complement is used.

    The equation system has the following size: n_fc+n_fm+n_vc+n_vm+n_src_c+n_src_v.
    The Schur complement split the system in two subsystems:
        - n_fc+n_fm (diagonal block)
        - n_vc+n_vm+n_src_c+n_src_v
    """

    # split the system (Schur complement split)
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


def _get_system_multiply_electric(sol, rhs_add, freq, A_c, A_src, R_vec_c, L_op_c):
    """
    Multiply the full equation matrix with a given solution test vector.

    For the multiplication of the dense matrix, the provided linear operators are used.
    The equation system has the following size: n_fc+n_fm+n_vc+n_vm+n_src_c+n_src_v.
    """

    # get the matrices
    (A_kvl_c, A_kcl_c) = A_c
    (A_vc_src, A_src_vc, A_src_src) = A_src

    # get the system size
    (n_vc, n_fc) = A_kcl_c.shape
    (n_src, n_src) = A_src_src.shape

    # get the angular frequency
    s = 1j*2*np.pi*freq

    # split the solution vector
    I_fc = sol[0:n_fc]
    V_vc = sol[n_fc:n_fc+n_vc]
    I_src = sol[n_fc+n_vc:n_fc+n_vc+n_src]

    # electric KVL equations
    rhs_1 = s*L_op_c(I_fc)
    rhs_2 = R_vec_c*I_fc
    rhs_3 = A_kvl_c*V_vc
    rhs_fc = rhs_1+rhs_2+rhs_3

    # electric KCL equations
    rhs_1 = A_kcl_c*I_fc
    rhs_2 = A_vc_src*I_src
    rhs_vc = rhs_1+rhs_2

    # form the source equation
    rhs_1 = A_src_vc*V_vc
    rhs_2 = A_src_src*I_src
    rhs_src = rhs_1+rhs_2

    # assemble the solution
    rhs = np.concatenate((rhs_fc, rhs_vc, rhs_src))+rhs_add

    return rhs


def _get_system_multiply_magnetic(sol, rhs_add, freq, A_m, R_vec_m, P_op_m):
    """
    Multiply the full equation matrix with a given solution test vector.

    For the multiplication of the dense matrix, the provided linear operators are used.
    The equation system has the following size: n_fc+n_fm+n_vc+n_vm+n_src_c+n_src_v.
    """

    # get the matrices
    (A_kvl_m, A_kcl_m) = A_m

    # get the system size
    (n_vm, n_fm) = A_kcl_m.shape

    # get the derivative operator (avoid singularity for DC solution)
    if freq == 0:
        s_diff = 1
    else:
        s_diff = 1j*2*np.pi*freq

    # split the solution vector
    I_fm = sol[0:n_fm]
    V_vm = sol[n_fm:n_fm+n_vm]

    # magnetic KVL equations
    rhs_1 = R_vec_m/s_diff*I_fm
    rhs_2 = A_kvl_m*V_vm
    rhs_fm = rhs_1+rhs_2

    # magnetic KCL equations
    rhs_1 = P_op_m(A_kcl_m*I_fm)
    rhs_2 = s_diff*V_vm
    rhs_vm = rhs_1+rhs_2

    # assemble the solution
    rhs = np.concatenate((rhs_fm, rhs_vm))+rhs_add

    return rhs


def _get_system_size(freq, A_c, A_m, A_src):
    """
    Get the size of the equation system and a scaling vector for the solution.

    The equation system has the following size: n_fc+n_fm+n_vc+n_vm+n_src_c+n_src_v.
    The scaling vector is required for the following reasons:
        - for avoid division per zero, the DC and AC system are slightly different
        - the DC system is using the magnetic flux as a variable
        - the AC system is using the derivative of the magnetic flux as a variable
        - the solution is using the magnetic flux as a variable
        - the scaling vector is used to match this discrepancy
    """

    # get the matrices
    (A_kvl_c, A_kcl_c) = A_c
    (A_kvl_m, A_kcl_m) = A_m
    (A_vc_src, A_src_vc, A_src_src) = A_src

    # get the system size
    (n_vc, n_fc) = A_kcl_c.shape
    (n_vm, n_fm) = A_kcl_m.shape
    (n_src, n_src) = A_src_src.shape

    # get the system size
    n_dof = n_vc+n_fc+n_vm+n_fm+n_src

    # get the angular frequency
    s = 1j*2*np.pi*freq

    if freq == 0:
        scaler = np.ones(n_dof, dtype=np.complex128)
    else:
        scaler_c = np.ones(n_fc+n_vc+n_src, dtype=np.complex128)
        scaler_fm = s*np.ones(n_fm, dtype=np.complex128)
        scaler_vm = np.ones(n_vm, dtype=np.complex128)
        scaler = np.concatenate((scaler_c, scaler_fm, scaler_vm))

    return n_dof, scaler


def get_source_vector(idx_vc, idx_vm, idx_fc, idx_fm, I_src_c, V_src_v):
    """
    Construct the right-hand side with the current and voltage sources.

    The right-hand size vector has the following size: n_fc+n_fm+n_vc+n_vm+n_src_c+n_src_v.
    The excitations are only located in the last equations: n_src_c+n_src_v.
    """

    # extract the voxel data
    n_c = len(idx_vc)+len(idx_fc)
    n_m = len(idx_vm)+len(idx_fm)

    # excitation are handled separately
    rhs_c = np.zeros(n_c, dtype=np.complex128)
    rhs_m = np.zeros(n_m, dtype=np.complex128)

    # assemble
    rhs = np.concatenate((rhs_c, I_src_c, V_src_v, rhs_m))

    return rhs


def get_kvl_kcl_matrix(A_net):
    """
    Construct the connection matrices for the KVL and KCL equations.

    The A_kvl matrix has the following size: (n_f, n_v).
    The A_kcl matrix has the following size: (n_v, n_f).
    """

    # connection matrix for the KCL
    A_kcl = +1*A_net

    # connection matrix for the KVL
    A_kvl = -1*A_net.transpose()

    return A_kvl, A_kcl


def get_source_matrix(idx_vc, idx_vm, idx_src_c, idx_src_v, G_src_c, R_src_v):
    """
    Construct the source matrices.
    The source matrices describes the sources (internal resistances/admittances).
    The source matrices connect the sources to the rest of the system.

    The source matrices have the following sizes:
        - A_vc_src: (n_vc, n_src_c+n_src_v)
        - A_src_vc: (n_src_c+n_src_v, n_vc)
        - A_src_src: (n_src_c+n_src_v, n_src_c+n_src_v)

    It should be noted that the matrices connecting the magnetic voxels are all-zeros.
    This is explained by the fact that the sources are only connected to electric voxels.
    """

    # extract the voxel data
    n_vc = len(idx_vc)
    n_vm = len(idx_vm)
    n_src_c = len(idx_src_c)
    n_src_v = len(idx_src_v)

    # find the variable indices
    idx_s = np.argsort(idx_vc)
    idx_src_c_p = np.searchsorted(idx_vc[idx_s], idx_src_c)
    idx_src_v_p = np.searchsorted(idx_vc[idx_s], idx_src_v)
    idx_src_c_local = idx_s[idx_src_c_p]
    idx_src_v_local = idx_s[idx_src_v_p]

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
    A_vc_src = sps.csc_matrix((val, (idx_row, idx_col)), shape=(n_vc, n_src_c+n_src_v), dtype=np.float64)

    # matrix between the source equations and the potential variables
    idx_row = np.concatenate((idx_src_v_add, idx_src_c_add))
    idx_col = np.concatenate((idx_src_v_local, idx_src_c_local))
    val = np.concatenate((cst_src_v, G_src_c))
    A_src_vc = sps.csc_matrix((val, (idx_row, idx_col)), shape=(n_src_c+n_src_v, n_vc), dtype=np.float64)

    # matrix between the source equations and the source variables
    idx_row = np.concatenate((idx_src_c_add, idx_src_v_add))
    idx_col = np.concatenate((idx_src_c_add, idx_src_v_add))
    val = np.concatenate((cst_src_c, R_src_v))
    A_src_src = sps.csc_matrix((val, (idx_row, idx_col)), shape=(n_src_c+n_src_v, n_src_c+n_src_v), dtype=np.float64)

    return A_vc_src, A_src_vc, A_src_src


def get_cond_operator(freq, A_c, A_m, A_src, R_vec_c, R_vec_m, L_vec_c, P_vec_m, K_op_c, K_op_m):
    """
    Get a linear operator that solves the preconditioner equation system.
    This operator is used as a preconditioner for the iterative method solving the full system.
    The Schur complement matrix of the preconditioner is also returned.
    This matrix is used to assess the condition number of the system.
    """

    # get the system size and the solution scaling
    (n_dof, sol_scaler) = _get_system_size(freq, A_c, A_m, A_src)

    # get the Schur complement
    (Y_mat_c, S_mat_c, S_fact_c, A_12_mat_c, A_21_mat_c) = _get_cond_fact_electric(freq, A_c, R_vec_c, L_vec_c, A_src)
    (Y_mat_m, S_mat_m, S_fact_m, A_12_mat_m, A_21_mat_m) = _get_cond_fact_magnetic(freq, A_m, R_vec_m, P_vec_m)

    # if the matrix is singular, there is not preconditioner
    if (not S_fact_c.get_status()) or (not S_fact_m.get_status()):
        return None, S_mat_c, S_mat_m

    # function describing the preconditioner
    def fct(rhs):
        (rhs_c, rhs_m) = _get_split_rhs(rhs, A_c, A_m, A_src)

        sol_c = _get_cond_solve(rhs_c, Y_mat_c, S_fact_c, A_12_mat_c, A_21_mat_c)

        sol_m = _get_cond_solve(rhs_m, Y_mat_m, S_fact_m, A_12_mat_m, A_21_mat_m)

        sol = _get_assemble_sol(sol_c, sol_m, A_c, A_m, A_src)

        sol = sol/sol_scaler
        return sol


    # rhs_test = np.arange(n_dof)
    # sol_test = fct(rhs_test)
    # sol_test_cmp = fct_new(rhs_test)

    # corresponding linear operator
    op = sla.LinearOperator((n_dof, n_dof), matvec=fct)

    return op, S_mat_c, S_mat_m


def get_system_operator(freq, A_c, A_m, A_src, R_vec_c, R_vec_m, L_op_c, P_op_m, K_op_c, K_op_m):
    """
    Get a linear operator that produce the matrix-vector multiplication result for the full system.
    This operator is used for the iterative solver.
    """

    # get the system size and the solution scaling
    (n_dof, sol_scaler) = _get_system_size(freq, A_c, A_m, A_src)

    # function describing the equation system
    def fct(sol):
        sol = sol*sol_scaler

        (sol_c, sol_m) = _get_split_sol(sol, A_c, A_m, A_src)

        (rhs_add_c, rhs_add_m) = _get_update_rhs(sol_c, sol_m, freq, A_c, A_m, A_src, K_op_c, K_op_m)

        rhs_c = _get_system_multiply_electric(sol_c, rhs_add_c, freq, A_c, A_src, R_vec_c, L_op_c)
        rhs_m = _get_system_multiply_magnetic(sol_m, rhs_add_m, freq, A_m, R_vec_m, P_op_m)

        rhs = np.concatenate((rhs_c, rhs_m))

        return rhs


    # corresponding linear operator
    op = sla.LinearOperator((n_dof, n_dof), matvec=fct)

    return op
