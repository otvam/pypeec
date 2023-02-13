"""
Different functions for extracting the fields and terminal currents and voltages from the solution vector.

The voxel structure has the following size: (nx, ny, nz).
The problem contains n_vc non-empty electric voxels and n_vm non-empty magnetic voxels.
The problem contains n_fc internal electric faces and n_fm internal magnetic faces.
The problem contains n_src_c current source voxels and n_src_v voltage source voxels.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np
from PyPEEC.lib_utils import timelogger

# get a logger
logger = timelogger.get_logger("SOLUTION")


def _get_vector_density(n, d, A_vox, var_f_all):
    """
    Project a face vector variable into a voxel vector variable.
    Scale the variable with respect to the face area (density).

    At the input, the array has the following size: 3*nx*ny*nx.
    At the output, the array has the following size: (nx*ny*nx, 3).
    """

    # extract the voxel data
    (dx, dy, dz) = d

    # project the faces into the voxels
    var_v_x = 0.5*np.abs(A_vox[:, 0*n:1*n])*var_f_all[0*n:1*n]
    var_v_y = 0.5*np.abs(A_vox[:, 1*n:2*n])*var_f_all[1*n:2*n]
    var_v_z = 0.5*np.abs(A_vox[:, 2*n:3*n])*var_f_all[2*n:3*n]

    # convert to density.
    var_v_x = var_v_x/(dy*dz)
    var_v_y = var_v_y/(dx*dz)
    var_v_z = var_v_z/(dx*dy)

    # assemble the variables
    var_v_all = np.stack((var_v_x, var_v_y, var_v_z), axis=1)

    return var_v_all


def _get_vector_divergence(d, A_vox, var_f_all):
    """
    Compute the divergence of a face vector with respect to the voxels.
    Scale the variable with respect to the voxel volume (density).

    At the input, the array has the following size: 3*nx*ny*nx.
    At the output, the array has the following size: nx*ny*nx.
    """

    # extract the voxel data
    (dx, dy, dz) = d

    # compute the divergence
    var_v_all = A_vox * var_f_all

    # convert to density.
    var_v_all = var_v_all/(dx*dy*dz)

    return var_v_all


def get_sol_extract(idx_fc, idx_fm, idx_vc, idx_vm, idx_src_c, idx_src_v, sol):
    """
    Split the solution vector into different variables.

    The solution vector is set in the following order:
        - n_fc: electric face currents
        - n_vc: electric voxel potentials
        - n_src: source currents
        - n_fm: magnetic face fluxes
        - n_vm: magnetic voxel potentials
    """

    # extract the voxel data
    n_fc = len(idx_fc)
    n_fm = len(idx_fm)
    n_vc = len(idx_vc)
    n_vm = len(idx_vm)
    n_src = len(idx_src_c)+len(idx_src_v)

    # split the solution vector
    I_fc = sol[0:n_fc]
    V_vc = sol[n_fc:n_fc+n_vc]
    I_src = sol[n_fc+n_vc:n_fc+n_vc+n_src]
    I_fm = sol[n_fc+n_vc+n_src:n_fc+n_vc+n_src+n_fm]
    V_vm = sol[n_fc+n_vc+n_src+n_fm:n_fc+n_vc+n_src+n_fm+n_vm]

    return I_fc, I_fm, V_vc, V_vm, I_src


def get_flow_density(n, d, idx_v, idx_f, A_vox, I_f):
    """
    Get the voxel flow from the face flow.
    Scale the flow with respect to the face area (density).

    At the input, the face flow vector has the following size: n_f.
    At the output, the voxel flow vector has the following size: (n_v, 3).
    """

    # extract the voxel data
    (nx, ny, nz) = n
    nv = nx*ny*nz

    # extend the solution for the complete voxel structure (including the empty voxels)
    I_f_all = np.zeros(3*nv, dtype=np.complex128)
    I_f_all[idx_f] = I_f

    # project the face currents into the voxels (scalar field)
    I_flow_v_all = _get_vector_density(nv, d, A_vox, I_f_all)

    # remove empty voxels
    I_flow_v = I_flow_v_all[idx_v]

    return I_flow_v


def get_flow_divergence(n, d, idx_v, idx_f, A_vox, I_f):
    """
    Get the divergence of a face flow with respect to the voxels.
    Scale the divergence with respect to the voxel volume (density).

    At the input, the face flow vector has the following size: n_f.
    At the output, the divergence vector has the following size: n_v.
    """

    # extract the voxel data
    (nx, ny, nz) = n
    nv = nx*ny*nz

    # extend the solution for the complete voxel structure (including the empty voxels)
    I_f_all = np.zeros(3*nv, dtype=np.complex128)
    I_f_all[idx_f] = I_f

    # compute the divergence
    I_div_v_all = _get_vector_divergence(d, A_vox, I_f_all)

    # remove empty voxels
    I_div_v = I_div_v_all[idx_v]

    return I_div_v


def get_integral(freq, I_fc, I_fm, R_vec_c, R_vec_m, L_op_c, K_op_c):
    """
    Sum the loss/energy in order to obtain global quantities.
    """

    # get the angular frequency
    s = 1j*2*np.pi*freq

    # get the magnetic losses linked with the electric domains
    P_fc = 0.5*np.conj(I_fc)*R_vec_c*I_fc

    # get the magnetic losses linked with the magnetic domains
    P_fm = 0.5*np.conj(s*I_fm)*R_vec_m*(I_fm)

    # get the magnetic energy linked with the electric domains
    W_fc = 0.5*np.conj(I_fc)*L_op_c(I_fc)

    # get the magnetic energy linked with the magnetic domains
    W_fm = 0.5*np.conj(I_fc)*K_op_c(I_fm)

    # compute the integral quantities
    P_electric = np.sum(np.real(P_fc))
    P_magnetic = np.sum(np.real(P_fm))
    W_electric = np.sum(np.real(W_fc))
    W_magnetic = np.sum(np.real(W_fm))
    P_tot = P_electric+P_magnetic
    W_tot = W_electric+W_magnetic

    # assign the integral quantities
    integral = {
        "P_electric": P_electric, "P_magnetic": P_magnetic, "P_tot": P_tot,
        "W_electric": W_electric, "W_magnetic": W_magnetic, "W_tot": W_tot,
    }

    # display
    logger.info("integral: P_electric = %.3e W" % P_electric)
    logger.info("integral: P_magnetic = %.3e W" % P_magnetic)
    logger.info("integral: W_electric = %.3e J" % W_electric)
    logger.info("integral: W_magnetic = %.3e J" % W_magnetic)
    logger.info("integral: P_tot = %.3e W" % P_tot)
    logger.info("integral: W_tot = %.3e J" % W_tot)

    return integral


def get_sol_extend(n, idx_src_c, idx_src_v, idx_vc, V_vc, I_src):
    """
    Expand the electric potential and source currents for all the voxels.

    The solution is assigned to all the voxels (even the empty voxels).
    The input electric potential vector has the following size: n_vc.
    The input source current vector has the following size: n_src_c+n_src_v.
    The output vectors have the following size: nx*ny*nz.
    """

    # extract the voxel data
    (nx, ny, nz) = n
    nv = nx*ny*nz

    # split the source currents between the current and voltage sources
    n_src_c = len(idx_src_c)
    n_src_v = len(idx_src_v)
    I_src_c = I_src[0:n_src_c]
    I_src_v = I_src[n_src_c:n_src_c+n_src_v]

    # assign voxel potentials
    V_v_all = np.zeros(nv, dtype=np.complex128)
    V_v_all[idx_vc] = V_vc

    # assign current source currents
    I_src_c_all = np.zeros(nv, dtype=np.complex128)
    I_src_c_all[idx_src_c] = I_src_c

    # assign voltage source currents
    I_src_v_all = np.zeros(nv, dtype=np.complex128)
    I_src_v_all[idx_src_v] = I_src_v

    return V_v_all, I_src_c_all, I_src_v_all


def get_terminal(source_idx, V_v_all, I_src_c_all, I_src_v_all):
    """
    Parse the terminal voltages and currents for the sources.
    The sources have internal resistances/admittances.
    Therefore, the extract value can differ from the source value.
    The results are assigned to a dict with the voltage and current values.
    """

    # init terminal dict
    terminal = dict()

    # parse the current source terminals
    for tag, dat_tmp in source_idx.items():
        # get the data
        source_type = dat_tmp["source_type"]
        idx = dat_tmp["idx"]

        # append the source
        if len(idx) == 0:
            I_tmp = np.nan+1j*np.nan
            V_tmp = np.nan+1j*np.nan
        else:
            # voltage is the average between all the voxels composing the terminal
            V_tmp = np.complex128(np.mean(V_v_all[idx]))

            # current is the sum between all the voxels composing the terminal
            if source_type == "current":
                I_tmp = np.complex128(np.sum(I_src_c_all[idx]))
            elif source_type == "voltage":
                I_tmp = np.complex128(np.sum(I_src_v_all[idx]))
            else:
                raise ValueError("invalid terminal type")

        # assign the current and voltage
        terminal[tag] = {"V": V_tmp, "I": I_tmp}

        # display
        V_str = "%.3e + %.3ej" % (V_tmp.real, V_tmp.imag)
        I_str = "%.3e + %.3ej" % (I_tmp.real, I_tmp.imag)
        logger.info("terminal: %s : V = %s V / I = %s A" % (tag, V_str, I_str))

    return terminal
