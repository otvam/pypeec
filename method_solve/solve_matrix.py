import numpy as np


def get_conductor_geometry(conductor):
    # get the indices of the conducting voxels and the resistivity
    idx_c = np.array([], dtype=np.int64)
    rho_c = np.array([], dtype=np.float64)
    for dat_tmp in conductor:
        idx = dat_tmp["idx"]
        rho = dat_tmp["rho"]

        idx_c = np.append(idx_c, np.array(idx))
        rho_c = np.append(rho_c, np.full(len(idx), rho))

    return idx_c, rho_c

def get_source_geomtry(src_current, src_voltage):

    # get the indices of the current source voxels
    idx_src_c = np.array([], dtype=np.int64)
    val_src_c = np.array([], dtype=np.float64)
    for dat_tmp in src_current:
        idx = dat_tmp["idx"]
        value = dat_tmp["value"]

        idx_src_c = np.append(idx_src_c, np.array(idx))
        val_src_c = np.append(val_src_c, np.full(len(idx), value/len(idx)))

    # get the indices of the voltage source voxels
    idx_src_v = np.array([], dtype=np.int64)
    val_src_v = np.array([], dtype=np.float64)
    for dat_tmp in src_voltage:
        idx = dat_tmp["idx"]
        value = dat_tmp["value"]

        idx_src_v = np.append(idx_src_v, np.array(idx))
        val_src_v = np.append(val_src_v, np.full(len(idx), value))

    return idx_src_c, val_src_c, idx_src_v, val_src_v