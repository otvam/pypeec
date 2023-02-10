"""
Different functions for extracting the fields and terminal currents and voltages from the solution vector.

The voxel structure has the following size: (nx, ny, nz).
The problem contains n_v non-empty voxels and n_f internal faces.
The problem contains n_src_c current source voxels and n_src_v voltage source voxels.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np
from PyPEEC.lib_utils import timelogger

# get a logger
logger = timelogger.get_logger("SOLUTION")


def _get_scalar_density(n, d, A_vox, var_f_all):
    """
    Project a face vector variable into a voxel scalar variable.
    Scale the variable with respect to the voxel volumes (density).

    At the input, the array has the following size: 3*nx*ny*nx.
    At the output, the array has the following size: nx*ny*nx.
    """

    # extract the voxel data
    (dx, dy, dz) = d

    # project the faces into the voxels
    var_v_all = 0.5*np.abs(A_vox[:, 0*n:3*n])*var_f_all[0*n:3*n]

    # convert to density.
    var_v_all = var_v_all/(dx*dy*dz)

    return var_v_all


def _get_vector_flux(n, d, A_vox, var_f_all):
    """
    Project a face vector variable into a voxel vector variable.
    Scale the variable with respect to the face areas (density).

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


def get_sol_extract(idx_fc, idx_fm, idx_vc, idx_vm, idx_src_c, idx_src_v, sol):
    """
    Split the solution vector into different variables.

    The solution vector is set in the following order:
        - n_f: face currents
        - n_v: voxel potentials
        - n_src_c: current source currents
        - n_src_v: voltage source currents
    """

    # extract the voxel data
    n_fc = len(idx_fc)
    n_fm = len(idx_fm)
    n_vc = len(idx_vc)
    n_vm = len(idx_vm)
    n_src = len(idx_src_c)+len(idx_src_v)

    # split the excitation vector
    I_fc = sol[0:n_fc]
    I_fm = sol[n_fc:n_fc+n_fm]
    V_vc = sol[n_fc+n_fm:n_fc+n_fm+n_vc]
    V_vm = sol[n_fc+n_fm+n_vc:n_fc+n_fm+n_vc+n_vm]
    I_src = sol[n_fc+n_fm+n_vc+n_vm:n_fc+n_fm+n_vc+n_vm+n_src]

    return I_fc, I_fm, V_vc, V_vm, I_src


def get_sol_extend(n, idx_src_c, idx_src_v, idx_vc, V_vc, I_src):
    """
    Expand the potential and source currents for all the voxels.

    The solution is assigned to all the voxels (even the empty voxels).
    The input vectors have the following size: n_v.
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


def get_current_density(n, d, idx_v, idx_f, A_vox, I_f):
    """
    Get the voxel current densities from the face currents.
    Scale the currents into current densities.

    At the input, the face current vector has the following size: n_f.
    At the output, the current density vector has the following size: (n_v, 3).
    """

    # extract the voxel data
    (nx, ny, nz) = n
    nv = nx*ny*nz

    # extend the solution for the complete voxel structure (including the empty voxels)
    I_f_all = np.zeros(3*nv, dtype=np.complex128)
    I_f_all[idx_f] = I_f

    # project the face currents into the voxels (scalar field)
    J_v_all = _get_vector_flux(nv, d, A_vox, I_f_all)

    # remove empty voxels
    J_v = J_v_all[idx_v]

    return J_v


def get_integral(I_fc, I_fm, R_vec_c, L_op_c, K_op_c):
    """
    Sum the loss/energy in order to obtain global quantities.
    """

    # get the losses for the different faces
    P_f = 0.5*np.conj(I_fc)*R_vec_c*I_fc

    # get the energy for the different faces
    M_fc = L_op_c(I_fc)
    M_fm = K_op_c(I_fm)

    # get the energy for the different faces
    W_f = 0.5*np.conj(I_fc)*(M_fc+M_fm)

    # compute the integral quantities
    P_tot = np.sum(np.real(P_f))
    W_tot = np.sum(np.real(W_f))

    # assign the integral quantities
    integral = {"P_tot": P_tot, "W_tot": W_tot}

    # display
    logger.info("integral: P_tot = %.3e W" % P_tot)
    logger.info("integral: W_tot = %.3e J" % W_tot)

    return integral


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
        logger.info("terminal: %s : V = %s V : I = %s A" % (tag, V_str, I_str))

    return terminal
