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


def _get_project_vector_voxel(n, A_incidence, var_f):
    """
    Project a face variable into the voxels (separately for the x, y, z components).
    A face is shared between two voxels (for the internal faces).
    The contributions are divided 50/50 between the two voxels.
    """

    var_v_x = 0.5*np.abs(A_incidence[:, 0*n:1*n])*var_f[0*n:1*n]
    var_v_y = 0.5*np.abs(A_incidence[:, 1*n:2*n])*var_f[1*n:2*n]
    var_v_z = 0.5*np.abs(A_incidence[:, 2*n:3*n])*var_f[2*n:3*n]

    return var_v_x, var_v_y, var_v_z


def _get_project_scalar_voxel(A_incidence, var_f):
    """
    Project a face variable into the voxels (sum of the x, y, z, components).
    A face is shared between two voxels (for the internal faces).
    The contributions are divided 50/50 between the two voxels.
    """

    var_v = 0.5*np.abs(A_incidence)*var_f

    return var_v


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

    # assign voxel voltages
    V_v = sol[n_f:n_f+n_v]

    # assign current source currents
    I_src_c = sol[n_f+n_v:n_f+n_v+n_src_c]

    # assign voltage source currents
    I_src_v = sol[n_f+n_v+n_src_c:n_f+n_v+n_src_c+n_src_v]

    return I_f, V_v, I_src_c, I_src_v


def get_sol_extend(n, idx_v, idx_src_c, idx_src_v, V_v, I_src_c, I_src_v):
    """
    Extract the voltage/current source currents.

    The solution is assigned to all the faces and voxels (even the empty faces/voxels).
    The voltage/current source current vector has the following size: nx*ny*nz.
    """

    # extract the voxel data
    (nx, ny, nz) = n
    n = nx * ny * nz

    # assign voxel voltages
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
    Combine the currents of all the internal faces of a voxel into a single vector.
    Scale the currents into current densities.

    At the input, the face current vector has the following size: 3*nx*ny*nz.
    At the output, the current density vector has the following size: (nx*ny*nz, 3).
    """

    # extract the voxel data
    (nx, ny, nz) = n
    (dx, dy, dz) = d
    n = nx*ny*nz

    # extend the solution for the complete voxel structure (including the empty voxels)
    I_f_all = np.zeros(3*n, dtype=np.complex128)
    I_f_all[idx_f] = I_f

    # project the face currents into the voxels
    (I_v_x, I_v_y, I_v_z) = _get_project_vector_voxel(n, A_incidence, I_f_all)

    # convert currents into current densities
    J_v_x = I_v_x/(dy*dz)
    J_v_y = I_v_y/(dx*dz)
    J_v_z = I_v_z/(dx*dy)

    # assemble voxel current densities
    J_v_all = np.stack((J_v_x, J_v_y, J_v_z), axis=1, dtype=np.complex128)

    # remove empty voxels
    J_v = J_v_all[idx_v, :]

    return J_v


def get_loss_density(n, d, idx_v, idx_f, A_incidence, R_vector, I_f):

    # extract the voxel data
    (nx, ny, nz) = n
    (dx, dy, dz) = d
    n = nx * ny * nz

    # get the face losses
    P_f = 0.5*np.conj(I_f)*R_vector*I_f

    # remove numerical errors
    P_f = np.real(P_f)

    # extend the solution for the complete voxel structure (including the empty voxels)
    P_f_all = np.zeros(3*n, dtype=np.float64)
    P_f_all[idx_f] = P_f

    # project the losses into the voxels
    P_v_all = _get_project_scalar_voxel(A_incidence, P_f_all)

    # convert losses into loss densities
    P_v_all = P_v_all/(dx*dy*dz)

    # remove empty voxels
    P_v = P_v_all[idx_v]

    return P_v


def get_energy_density(n, d, idx_v, idx_f, A_incidence, L_tensor, I_f):

    # extract the voxel data
    (nx, ny, nz) = n
    (dx, dy, dz) = d
    n = nx * ny * nz

    # compute the FFT circulant tensor (in order to make matrix-vector multiplication with FFT)
    L_tensor = fourier_transform.get_circulant_tensor(L_tensor)

    # multiply the inductance matrix with the current vector (done with the FFT circulant tensor)
    P_f = fourier_transform.get_circulant_multiply(L_tensor, idx_f, I_f)

    # get the face energy
    W_f = 0.5*np.conj(I_f)*P_f

    # remove numerical errors
    W_f = np.real(W_f)

    # extend the solution for the complete voxel structure (including the empty voxels)
    W_f_all = np.zeros(3*n, dtype=np.float64)
    W_f_all[idx_f] = W_f

    # project the energy into the voxels
    W_v_all = _get_project_scalar_voxel(A_incidence, W_f_all)

    # convert energy into energy density
    W_v_all = W_v_all/(dx*dy*dz)

    # remove empty voxels
    W_v = W_v_all[idx_v]

    return W_v


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
