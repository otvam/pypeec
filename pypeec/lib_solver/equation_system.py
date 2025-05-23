"""
Different functions for building the equation system.

Two different equation systems are built:
    - A sparse system for the preconditioner.
    - A dense system for the iterative solver.

The voxel structure has the following size: (nx, ny, nz).
The problem contains n_vc non-empty electric voxels and n_vm non-empty magnetic voxels.
The problem contains n_fc internal electric faces and n_fm internal magnetic faces.
The problem contains n_src_c current source voxels and n_src_v voltage source voxels.

The equations are set in the following order:
    [
        n_fc        the electric KVL equations
        n_vc        the electric KCL equations
        n_src_c     the current source voxels equations (source equation with internal admittance)
        n_src_v     the voltage source voxels equations (source equation with internal impedance)
        n_fm        the magnetic KVL equations
        n_vm        the magnetic KCL equations
    ]

The complete solution vector is:
    [
        I_fc        n_fc        electric face currents        A
        V_vc        n_vc        electric voxel potentials     V
        I_src_c     n_src_c     current source currents       A
        I_src_v     n_src_v     voltage source currents       A
        I_fm        n_fm        magnetic face fluxes          V*s
        V_vm        n_vm        magnetic voxel potentials     A
    ]

The complete right-hand size vector is:
    [
        n_fc        zero excitation                V
        n_vc        zero excitation                A
        n_src_c     current source excitations     A
        n_src_v     voltage source excitations     V
        n_fm        zero excitation                A
        n_vm        zero excitation                A
    ]

The complete equation matrix is:
    [
        +R_c+s*L_c     -A_net_c'       +0                 +0                 +s*K_c           +0
        +A_net_c       +0              +A_vc_src_c        +A_vc_src_v        +0               +0
        +0             +A_src_c_vc     +A_src_c_src_c     +0                 +0               +0
        +0             +A_src_v_vc     +0                 +A_src_v_src_v     +0               +0
        -K_m           +0              +0                 +0                 +R_m             -A_net_m'
        +0             +0              +0                 +0                 +P_m*A_net_m     +I
    ]

The units of the equation matrix is:
    [
        Ohm            1               0                  0                  1/s              0
        1              0               1                  1                  0                0
        0              1/Ohm           1                  0                  0                0
        0              1               0                  Ohm                0                0
        1              0               0                  0                  A/V/s            1
        0              0               0                  0                  A/V/s            1
    ]

The matrices have the following description and units:
    [
        R_c               resistance matrix                             Ohm
        L_c               inductance matrix                             Henry
        R_m               magnetic resistance matrix                    1/Henry
        P_m               magnetic potential matrix                     1/Henry
        A_net_c           electric voxel incidence matrix               1
        A_net_m           magnetic voxel incidence matrix               1
        K_c               magnetic to electric coupling matrix          1
        K_m               electric to magnetic coupling matrix          1
        A_vc_src_c        current source current coupling               1
        A_vc_src_v        voltage source current coupling               1
        A_src_c_vc        admittance matrix for the current sources     1/Ohm
        A_src_v_vc        voltage source voltage coupling               1
        A_src_c_src_c     current source current coupling               1
        A_src_v_src_v     resistance matrix for the current sources     Ohm
    ]

For the DC problem (zero frequency), multiplication per zero are occurring.
Therefore, the problem is formulated slightly differently for this case.

It should be noted that surface charges are not considered.
Only volume charges are used, which is an approximation.

For the preconditioner, the following simplifications are made:
    - The dense inductance matrix is diagonalized.
    - The dense potential matrix is diagonalized.
    - The electric-magnetic coupling matrices are neglected.

With these assumptions, a sparse (electric and magnetic) equation system is obtained.
The preconditioner is solved separately for the electric and magnetic equations.

The preconditioner matrices (electric and magnetic) have the following form:
    [
        mat_11,    mat_12;
        mat_21,    mat_22;
    ]

The first block matrix (mat_11) is diagonal and the Schur complement can be used.

For the full equation system, the complete dense matrices are used:
    - The system is split in three parts: electric, magnetic, and electric-magnetic coupling.
    - The system is meant to be solved with an iterative matrix solver.
    - A matrix-vector operator describing the system is returned.

Warning
-------
    - For problems with magnetic domains, the preconditioner is not optimal.
    - This might lead to a slow convergence of the iterative matrix solver.
    - For such cases, using the segregated solver approach might be useful.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import numpy as np
import scipy.sparse as sps


def _get_coupling_electric(sol_m, freq, n_vc, n_fc, n_fm, n_src, K_op_c):
    """
    Compute the magnetic to electric couplings.
    The magnetic face currents are multiplied with the couplings matrices.
    The coupling contributions to the electric rhs vector are returned.

    The vectors have the following size: n_fc+n_vc+n_src_c+n_src_v.
    """

    # extract the face current
    I_fm = sol_m[0:n_fm]

    # get the angular frequency
    s = 1j * 2 * np.pi * freq

    # compute the couplings
    if freq == 0:
        cpl_fc = np.zeros(n_fc, dtype=np.complex128)
    else:
        cpl_fc = s * K_op_c(I_fm)

    cpl_vc = np.zeros(n_vc, dtype=np.complex128)
    cpl_src = np.zeros(n_src, dtype=np.complex128)

    # assemble the vectors
    cpl_c = np.concatenate((cpl_fc, cpl_vc, cpl_src))

    return cpl_c


def _get_coupling_magnetic(sol_c, n_fc, n_vm, K_op_m):
    """
    Compute the electric to magnetic couplings.
    The electric face currents are multiplied with the couplings matrices.
    The coupling contributions to the magnetic rhs vector are returned.

    The vectors have the following size: n_fm+n_vm.
    """

    # extract the face current
    I_fc = sol_c[0:n_fc]

    # compute the couplings
    cpl_fm = -K_op_m(I_fc)
    cpl_vm = np.zeros(n_vm, dtype=np.complex128)

    # assemble the vectors
    cpl_m = np.concatenate((cpl_fm, cpl_vm))

    return cpl_m


def _get_cond_fact_electric(freq, A_net_c, R_c, L_c, A_src):
    """
    Compute the sparse matrices using for the electric preconditioner.

    The equation system has the following size: n_fc+n_vc+n_src_c+n_src_v.
    The first (n_fc, n_fc) block is a diagonal matrix:
    """

    # get the matrices
    A_vc_src = A_src["A_vc_src"]
    A_src_vc = A_src["A_src_vc"]
    A_src_src = A_src["A_src_src"]

    # get the system size
    (n_vc, n_fc) = A_net_c.shape
    (n_src, n_src) = A_src_src.shape

    # get the angular frequency
    s = 1j * 2 * np.pi * freq

    # admittance matrix
    mat_11 = sps.diags(R_c + s * L_c, format="csc")

    # assemble the matrices
    mat_21 = A_net_c
    mat_12 = -A_net_c.transpose()
    mat_22 = sps.csc_matrix((n_vc, n_vc), dtype=np.int64)

    # expand for the source matrices
    A_add = sps.csc_matrix((n_fc, n_src), dtype=np.int64)
    mat_12 = sps.hstack([mat_12, A_add], dtype=np.complex128, format="csr")

    # expand for the source matrices
    A_add = sps.csc_matrix((n_src, n_fc), dtype=np.int64)
    mat_21 = sps.vstack([mat_21, A_add], dtype=np.complex128, format="csc")

    # add the source
    mat_22 = sps.bmat([[mat_22, A_vc_src], [A_src_vc, A_src_src]], dtype=np.complex128, format="csc")

    # assign the matrices
    pcd_mat = {"mat_11": mat_11, "mat_22": mat_22, "mat_12": mat_12, "mat_21": mat_21}

    return pcd_mat


def _get_cond_fact_magnetic(A_net_m, R_m, P_m):
    """
    Compute the sparse matrices using for the magnetic preconditioner.

    The equation system has the following size: n_fm+n_vm.
    The first (n_fm, n_fm) block is a diagonal matrix:
    """

    # get the system size
    (n_vm, n_fm) = A_net_m.shape

    # admittance matrix
    mat_11 = sps.diags(R_m, format="csc")

    # assemble the matrices
    mat_21 = P_m * A_net_m
    mat_12 = -A_net_m.transpose()
    mat_22 = sps.eye(n_vm, format="csc")

    # assign the matrices
    pcd_mat = {"mat_11": mat_11, "mat_22": mat_22, "mat_12": mat_12, "mat_21": mat_21}

    return pcd_mat


def _get_system_multiply_electric(sol, freq, A_net_c, A_src, R_c, L_op_c):
    """
    Multiply the full electric equation matrix with a given solution test vector.

    For the multiplication of the dense matrix, the provided linear operators are used.
    The equation system has the following size: n_fc+n_vc+n_src_c+n_src_v.
    """

    # get the matrices
    A_vc_src = A_src["A_vc_src"]
    A_src_vc = A_src["A_src_vc"]
    A_src_src = A_src["A_src_src"]

    # get the system size
    (n_vc, n_fc) = A_net_c.shape
    (n_src, n_src) = A_src_src.shape

    # get the angular frequency
    s = 1j * 2 * np.pi * freq

    # split the solution vector
    I_fc = sol[0:n_fc]
    V_vc = sol[n_fc : n_fc + n_vc]
    I_src = sol[n_fc + n_vc : n_fc + n_vc + n_src]

    # multiply the inductance matrix
    if freq == 0:
        rhs_kvl_ind = np.zeros(n_fc, dtype=np.complex128)
    else:
        rhs_kvl_ind = s * L_op_c(I_fc)

    # electric KVL equations
    rhs_kvl_res = R_c * I_fc
    rhs_kvl_net = -A_net_c.transpose() * V_vc

    # electric KCL equations
    rhs_kcl_net = A_net_c * I_fc
    rhs_kvl_src = A_vc_src * I_src

    # form the source equation
    rhs_src_con = A_src_vc * V_vc
    rhs_src_src = A_src_src * I_src

    # assemble the solution
    rhs_kvl = rhs_kvl_ind + rhs_kvl_res + rhs_kvl_net
    rhs_kcl = rhs_kcl_net + rhs_kvl_src
    rhs_src = rhs_src_con + rhs_src_src
    rhs = np.concatenate((rhs_kvl, rhs_kcl, rhs_src))

    return rhs


def _get_system_multiply_magnetic(sol, A_net_m, R_m, P_op_m):
    """
    Multiply the full magnetic equation matrix with a given solution test vector.

    For the multiplication of the dense matrix, the provided linear operators are used.
    The equation system has the following size: n_fm+n_vm.
    """

    # get the system size
    (n_vm, n_fm) = A_net_m.shape

    # split the solution vector
    I_fm = sol[0:n_fm]
    V_vm = sol[n_fm : n_fm + n_vm]

    # multiply the potential matrix
    rhs_kcl_pot = P_op_m(A_net_m * I_fm)

    # get the term that are different for DC and AC cases
    rhs_kvl_res = R_m * I_fm
    rhs_kcl_net = V_vm

    # magnetic KVL equations
    rhs_kvl_net = -A_net_m.transpose() * V_vm

    # assemble the solution
    rhs_kvl = rhs_kvl_res + rhs_kvl_net
    rhs_kcl = rhs_kcl_pot + rhs_kcl_net
    rhs = np.concatenate((rhs_kvl, rhs_kcl))

    return rhs


def get_source_vector(idx_vc, idx_vm, idx_fc, idx_fm, I_src_c, V_src_v):
    """
    Construct the right-hand side with the current and voltage sources.

    The right-hand size vector has the following size: n_fc+n_fm+n_vc+n_vm+n_src_c+n_src_v.
    The excitations are only located in the last equations: n_src_c+n_src_v.
    """

    # extract the voxel data
    n_c = len(idx_vc) + len(idx_fc)
    n_m = len(idx_vm) + len(idx_fm)

    # excitation are handled separately
    rhs_c = np.zeros(n_c, dtype=np.complex128)
    rhs_m = np.zeros(n_m, dtype=np.complex128)

    # assemble
    rhs_c = np.concatenate((rhs_c, I_src_c, V_src_v))

    # combine the electric and magnetic data
    rhs_cm = (rhs_c, rhs_m)

    return rhs_cm


def get_source_matrix(idx_vc, idx_src_c, idx_src_v, Y_src_c, Z_src_v):
    """
    Construct the source matrices.
    The source matrices describes the sources (internal resistances/admittances).
    The source matrices connect the sources to the rest of the system.

    The source matrices have the following sizes:
        - A_vc_src which contains A_vc_src_c and A_vc_src_v: (n_vc, n_src_c+n_src_v).
        - A_src_vc which contains A_src_c_vc and A_src_v_vc: (n_src_c+n_src_v, n_vc).
        - A_src_src which contains A_src_c_src_c and A_src_v_src_v: (n_src_c+n_src_v, n_src_c+n_src_v).

    It should be noted that the matrices connecting the magnetic voxels are all-zeros.
    This is explained by the fact that the sources are only connected to electric voxels.
    """

    # extract the voxel data
    n_vc = len(idx_vc)
    n_src_c = len(idx_src_c)
    n_src_v = len(idx_src_v)

    # find the variable indices
    idx_s = np.argsort(idx_vc)
    idx_src_c_p = np.searchsorted(idx_vc, idx_src_c, sorter=idx_s)
    idx_src_v_p = np.searchsorted(idx_vc, idx_src_v, sorter=idx_s)
    idx_src_c_local = idx_s[idx_src_c_p]
    idx_src_v_local = idx_s[idx_src_v_p]

    # indices of the new source equations to be added
    idx_src_c_add = np.arange(0, n_src_c, dtype=np.int64)
    idx_src_v_add = np.arange(n_src_c, n_src_c + n_src_v, dtype=np.int64)

    # constant vector with the size of the sources
    cst_src_c = np.full(n_src_c, 1, dtype=np.complex128)
    cst_src_v = np.full(n_src_v, 1, dtype=np.complex128)

    # matrix between the KCL equations and the source variables
    idx_row = np.concatenate((idx_src_c_local, idx_src_v_local))
    idx_col = np.concatenate((idx_src_c_add, idx_src_v_add))
    val = np.concatenate((-cst_src_c, -cst_src_v))
    A_vc_src = sps.csc_matrix((val, (idx_row, idx_col)), shape=(n_vc, n_src_c + n_src_v), dtype=np.complex128)

    # matrix between the source equations and the potential variables
    idx_row = np.concatenate((idx_src_v_add, idx_src_c_add))
    idx_col = np.concatenate((idx_src_v_local, idx_src_c_local))
    val = np.concatenate((cst_src_v, Y_src_c))
    A_src_vc = sps.csc_matrix((val, (idx_row, idx_col)), shape=(n_src_c + n_src_v, n_vc), dtype=np.complex128)

    # matrix between the source equations and the source variables
    idx_row = np.concatenate((idx_src_c_add, idx_src_v_add))
    idx_col = np.concatenate((idx_src_c_add, idx_src_v_add))
    val = np.concatenate((cst_src_c, Z_src_v))
    A_src_src = sps.csc_matrix((val, (idx_row, idx_col)), shape=(n_src_c + n_src_v, n_src_c + n_src_v), dtype=np.complex128)

    # number of sources
    n_src = n_src_v + n_src_c

    # assign the matrices
    A_src = {"A_vc_src": A_vc_src, "A_src_vc": A_src_vc, "A_src_src": A_src_src}

    return A_src, n_src


def get_cond_operator(freq, A_net_c, A_net_m, A_src, R_c, R_m, L_c, P_m):
    """
    Get linear operators that solves the preconditioner equation system.
    These operators are used as a preconditioner for the iterative method solving the full system.

    The system is split between the electric and magnetic equations.
    The Schur complement matrices of the preconditioner can be used.
    These matrices are used to assess the condition number of the system.
    """

    # get the sparse system
    pcd_mat_c = _get_cond_fact_electric(freq, A_net_c, R_c, L_c, A_src)
    pcd_mat_m = _get_cond_fact_magnetic(A_net_m, R_m, P_m)

    # combine the electric and magnetic data (preconditioner)
    pcd_mat_cm = (pcd_mat_c, pcd_mat_m)

    return pcd_mat_cm


def get_coupling_operator(freq, n_vc, n_fc, n_vm, n_fm, n_src, K_op_c, K_op_m):
    """
    Get linear operators that represent the electric-magnetic couplings.

    The system is split between the electric and magnetic equations.
    These operators are coupling both systems.
    """

    # function describing the electric coupling
    def fct_c(sol_m):
        cpl_c = _get_coupling_electric(sol_m, freq, n_vc, n_fc, n_fm, n_src, K_op_c)
        return cpl_c

    # function describing the magnetic coupling
    def fct_m(sol_c):
        cpl_m = _get_coupling_magnetic(sol_c, n_fc, n_vm, K_op_m)
        return cpl_m

    # combine the electric and magnetic data
    fct_cm = (fct_c, fct_m)

    return fct_cm


def get_system_operator(freq, A_net_c, A_net_m, A_src, R_c, R_m, L_op_c, P_op_m):
    """
    Get linear operators that produce the matrix-vector multiplication result for the full system.
    These operators are used for the iterative solver.

    The system is split between the electric and magnetic equations.
    """

    # function describing the electric equation system
    def fct_c(sol_c):
        rhs_c = _get_system_multiply_electric(sol_c, freq, A_net_c, A_src, R_c, L_op_c)
        return rhs_c

    # function describing the magnetic equation system
    def fct_m(sol_m):
        rhs_m = _get_system_multiply_magnetic(sol_m, A_net_m, R_m, P_op_m)
        return rhs_m

    # combine the electric and magnetic data
    fct_cm = (fct_c, fct_m)

    return fct_cm


def get_system_sol_idx(idx_vc, idx_fc, idx_vm, idx_fm, n_src):
    """
    Get the indices of the vectors composing the solution.
    """

    # get the system size
    n_vc = len(idx_vc)
    n_fc = len(idx_fc)
    n_vm = len(idx_vm)
    n_fm = len(idx_fm)

    # init index dict
    sol_idx = {}

    # init the index offset
    n_offset = 0

    # get the electric variable
    sol_idx["I_fc"] = range(n_offset, n_offset + n_fc)
    n_offset += n_fc
    sol_idx["V_vc"] = range(n_offset, n_offset + n_vc)
    n_offset += n_vc
    sol_idx["I_src"] = range(n_offset, n_offset + n_src)
    n_offset += n_src

    # get the magnetic variable
    sol_idx["I_fm"] = range(n_offset, n_offset + n_fm)
    n_offset += n_fm
    sol_idx["V_vm"] = range(n_offset, n_offset + n_vm)
    n_offset += n_vm

    return sol_idx, n_vc, n_fc, n_vm, n_fm
