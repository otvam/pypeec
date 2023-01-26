"""
Different functions for extracting the fields and terminal currents and voltages from the solution vector.

The voxel structure has the following size: (nx, ny, nz).
The problem contains n_v non-empty voxels and n_f internal faces.
The problem contains n_src_c current source voxels and n_src_v voltage source voxels.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np
from PyPEEC.lib_matrix import fourier_transform
from PyPEEC.lib_utils import timelogger

# get a logger
logger = timelogger.get_logger("SOLUTION")


def _get_scalar_density(n, d, A_incidence, var_f_all):
    # extract the voxel data
    (dx, dy, dz) = d

    # project the faces into the voxels
    var_v_all = 0.5*np.abs(A_incidence[:, 0*n:3*n])*var_f_all[0*n:3*n]

    # scale the loss/energy into loss/energy densities.
    var_v_all = var_v_all/(dx*dy*dz)

    return var_v_all


def _get_vector_flux(n, d, A_incidence, var_f_all):
    # extract the voxel data
    (dx, dy, dz) = d

    # project the faces into the voxels
    var_v_x = 0.5*np.abs(A_incidence[:, 0*n:1*n])*var_f_all[0*n:1*n]
    var_v_y = 0.5*np.abs(A_incidence[:, 1*n:2*n])*var_f_all[1*n:2*n]
    var_v_z = 0.5*np.abs(A_incidence[:, 2*n:3*n])*var_f_all[2*n:3*n]

    # convert currents into current densities
    var_v_x = var_v_x/(dy*dz)
    var_v_y = var_v_y/(dx*dz)
    var_v_z = var_v_z/(dx*dy)

    # assemble voxel current densities
    var_v_all = np.stack((var_v_x, var_v_y, var_v_z), axis=1)

    return var_v_all


def _get_vector_density(n, d, A_incidence, var_f_all):
    # extract the voxel data
    (dx, dy, dz) = d

    # keep only the positive and negative faces
    A_incidence_pos = A_incidence[A_incidence == +1]
    A_incidence_neg = A_incidence[A_incidence == -1]

    # project the faces into the voxels
    var_v_x = 0.5*np.abs(A_incidence[:, 0*n:1*n])*var_f_all[0*n:1*n]
    var_v_y = 0.5*np.abs(A_incidence[:, 1*n:2*n])*var_f_all[1*n:2*n]
    var_v_z = 0.5*np.abs(A_incidence[:, 2*n:3*n])*var_f_all[2*n:3*n]

    # convert currents into current densities
    var_v_x = var_v_x/(dy*dz)
    var_v_y = var_v_y/(dx*dz)
    var_v_z = var_v_z/(dx*dy)

    # assemble voxel current densities
    var_v_all = np.stack((var_v_x, var_v_y, var_v_z), axis=1)

    return var_v_all


def get_sol_extract(idx_f, idx_v, idx_src_c, idx_src_v, sol):
    """
    Split the solution vector into different variables.

    The solution vector is set in the following order:
        - n_f: face currents
        - n_v: voxel potentials
        - n_src_c: current source currents
        - n_src_v: voltage source currents
    """

    # extract the voxel data
    n_v = len(idx_v)
    n_f = len(idx_f)
    n_src_c = len(idx_src_c)
    n_src_v = len(idx_src_v)

    # assign face currents
    I_f = sol[0:n_f]

    # assign voxel potentials
    V_v = sol[n_f:n_f+n_v]

    # assign current source currents
    I_src_c = sol[n_f+n_v:n_f+n_v+n_src_c]

    # assign voltage source currents
    I_src_v = sol[n_f+n_v+n_src_c:n_f+n_v+n_src_c+n_src_v]

    return I_f, V_v, I_src_c, I_src_v


def get_sol_extend(n, idx_v, idx_src_c, idx_src_v, V_v, I_src_c, I_src_v):
    """
    Expand the potential and source currents for all the voxels.

    The solution is assigned to all the voxels (even the empty voxels).
    The input vectors have the following size: n_v.
    The output vectors have the following size: nx*ny*nz.
    """

    # extract the voxel data
    (nx, ny, nz) = n
    n = nx*ny*nz

    # assign voxel potentials
    V_v_all = np.zeros(n, dtype=np.complex128)
    V_v_all[idx_v] = V_v

    # assign current source currents
    I_src_c_all = np.zeros(n, dtype=np.complex128)
    I_src_c_all[idx_src_c] = I_src_c

    # assign voltage source currents
    I_src_v_all = np.zeros(n, dtype=np.complex128)
    I_src_v_all[idx_src_v] = I_src_v

    return V_v_all, I_src_c_all, I_src_v_all


def get_current_density(n, d, idx_v, idx_f, A_incidence, I_f):
    """
    Get the voxel current densities from the face currents.
    Scale the currents into current densities.

    At the input, the face current vector has the following size: n_f.
    At the output, the current density vector has the following size: (nx*ny*nz, 3).
    """

    # extract the voxel data
    (nx, ny, nz) = n
    n = nx*ny*nz

    # extend the solution for the complete voxel structure (including the empty voxels)
    I_f_all = np.zeros(3*n, dtype=np.complex128)
    I_f_all[idx_f] = I_f

    # project the face currents into the voxels (scalar field)
    J_v_all = _get_vector_density(n, d, A_incidence, I_f_all)

    # remove empty voxels
    J_v = J_v_all[idx_v]

    return J_v


def get_drop_flux(idx_f, R_vector, L_tensor, I_f):
    """
    Get the resistive voltage drop and magnetic flux across the faces.
    At the input, the face current vector has the following size: n_f.
    At the output, the vectors have the following size: n_f.
    """

    # get the resistive voltage drop
    V_f = R_vector*I_f

    # compute the FFT circulant tensor (in order to make matrix-vector multiplication with FFT)
    L_tensor = fourier_transform.get_circulant_tensor(L_tensor)

    # get the energy for the different faces
    M_f = fourier_transform.get_circulant_multiply(L_tensor, idx_f, I_f)

    return V_f, M_f


def get_integral(V_f, M_f, I_f):
    """
    Sum the loss/energy in order to obtain global quantities.
    """

    # get the losses for the different faces
    P_f = 0.5*np.conj(I_f)*V_f

    # get the energy for the different faces
    W_f = 0.5*np.conj(I_f)*M_f

    # compute the integral quantities
    P_tot = np.sum(np.real(P_f))
    W_tot = np.sum(np.real(W_f))

    # assign the integral quantities
    integral = {"P_tot": P_tot, "W_tot": W_tot}

    # display
    logger.info("terminal: P_tot = %.3e W" % P_tot)
    logger.info("terminal: W_tot = %.3e J" % W_tot)

    return integral


def get_loss(n, d, idx_v, idx_f, A_incidence, V_f, I_f):
    """
    Get the loss densities for the voxels.

    At the input, the face current vector has the following size: n_f.
    At the output, the loss density vector has the following size: nx*ny*nz.
    """

    # extract the voxel data
    (nx, ny, nz) = n
    n = nx*ny*nz

    # get the losses for the different faces
    P_f = 0.5*np.conj(I_f)*V_f

    # extend the solution for the complete voxel structure (including the empty voxels)
    P_f_all = np.zeros(3*n, dtype=np.complex128)
    P_f_all[idx_f] = P_f

    # project the loss/energy from the faces into the voxels
    P_v_all = _get_scalar_density(n, d, A_incidence, P_f_all)

    # remove numerical errors (losses are real)
    P_v_all = np.real(P_v_all)

    # remove empty voxels
    P_v = P_v_all[idx_v]

    return P_v


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
