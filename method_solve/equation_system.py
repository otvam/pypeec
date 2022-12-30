import numpy as np
import scipy.sparse as sps
import scipy.special as sc


def get_source_vector(idx_v, idx_f, idx_src_c_local, val_src_c, val_src_v):
    # extract the voxel data
    n_v = len(idx_v)
    n_f = len(idx_f)

    # no excitation for the KVL
    b_src_zero = np.zeros(n_f, dtype=np.float64)

    # current sources are connected to the KCL
    b_src_current = np.zeros(n_v, dtype=np.float64)
    b_src_current[idx_src_c_local] = val_src_c

    # voltage sources are separate equations
    b_src_voltage = val_src_v

    # assemble
    b_src = np.concatenate((b_src_zero, b_src_current, b_src_voltage), dtype=np.float64)

    return b_src


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
