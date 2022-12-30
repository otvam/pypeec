import numpy as np
import scipy.sparse as sps
import scipy.sparse.linalg as lna
from method_solve import circulant_tensor


def get_source_vector(idx_v, idx_f, idx_src_c_local, val_src_c, val_src_v):
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

    # connection matrix for the source
    idx_add = np.arange(n_v, n_v+n_src_v, dtype=np.int64)
    idx_row = np.concatenate((idx_src_v_local, idx_add), dtype=np.int64)
    idx_col = np.concatenate((idx_add, idx_src_v_local), dtype=np.int64)
    data = np.concatenate((np.full(n_src_v, -1), np.full(n_src_v, +1)), dtype=np.int64)
    A_src = sps.csc_matrix((data, (idx_row, idx_col)), shape=(n_v+n_src_v, n_v+n_src_v), dtype=np.int64)

    return A_kcl, A_kvl, A_src


def get_preconditioner_decomposition(R_vector, ZL_vector, A_kcl, A_kvl, A_src):
    # admittance vector
    Y_vector = 1/(R_vector+ZL_vector)

    # admittance matrix
    Y_matrix = sps.diags(Y_vector)

    # computing the Schur complement (with respect to the diagonal admittance matrix)
    S_matrix = A_src-A_kcl*Y_matrix*A_kvl

    # compute the LU decomposition of the sparse Schur complement
    LU_decomposition = lna.splu(S_matrix)

    return Y_matrix, LU_decomposition


def get_preconditioner_solve(rhs, idx_v, idx_f, idx_src_v_local, A_kcl, A_kvl, Y_matrix, LU_decomposition):
    # get the matrix size
    n_a = len(idx_f)
    n_b = len(idx_v)+len(idx_src_v_local)

    # split the excitation vector
    rhs_a = rhs[0:n_a]
    rhs_b = rhs[n_a:n_a+n_b]

    # solve the equation system (Schur complement and LU decomposition)
    tmp = rhs_b-(A_kcl*(Y_matrix*rhs_a))
    sol_b = LU_decomposition.solve(tmp)
    sol_a = Y_matrix*(rhs_a-(A_kvl*sol_b))

    # assemble the solution
    sol = np.concatenate((sol_a, sol_b), dtype=np.complex128)

    return sol


def get_system_multiply(sol, n, idx_v, idx_f, idx_src_v_local, A_kcl, A_kvl, A_src, R_tensor, ZL_tensor):
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
        rhs_a_all[:, :, :, i] += circulant_tensor.get_multiply(ZL_tensor[:, :, :, i], sol_a_all[:, :, :, i])
        rhs_a_all[:, :, :, i] += R_tensor[:, :, :, i]*sol_a_all[:, :, :, i]

    # flatten the tensor into a vector
    rhs_a_all = rhs_a_all.flatten(order="F")

    # form the complete KVL
    rhs_a = rhs_a_all[idx_f]+A_kvl*sol_b

    # form the complete KCL
    rhs_b = A_kcl*sol_a+A_src*sol_b

    # assemble the solution
    rhs = np.concatenate((rhs_a, rhs_b), dtype=np.complex128)

    return rhs