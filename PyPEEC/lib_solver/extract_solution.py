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


def get_sol_extract(n, idx_f, idx_v, idx_src_c, idx_src_v, sol):
    """
    Extract the face currents, voxel potentials, and voltage/current source currents.

    The solution vector is set in the following order:
        - n_f: face currents
        - n_v: voxel potentials
        - n_src_c: current source currents
        - n_src_v: voltage source currents

    The solution is assigned to all the faces and voxels (even the empty faces/voxels).
    The face current vector has the following size: 3*nx*ny*nz.
    The voxel potential vector has the following size: nx*ny*nz.
    The voltage/current source current vector has the following size: nx*ny*nz.
    """

    # extract the voxel data
    (nx, ny, nz) = n
    n_v = len(idx_v)
    n_f = len(idx_f)
    n_src_c = len(idx_src_c)
    n_src_v = len(idx_src_v)
    n = nx*ny*nz

    # assign face currents
    I_f_all = np.zeros(3*n, dtype=np.complex128)
    I_f_all[idx_f] = sol[0:n_f]

    # assign voxel voltages
    V_v_all = np.zeros(n, dtype=np.complex128)
    V_v_all[idx_v] = sol[n_f:n_f+n_v]

    # assign current source currents
    I_src_c = np.zeros(n, dtype=np.complex128)
    I_src_c[idx_src_c] = sol[n_f+n_v:n_f+n_v+n_src_c]

    # assign voltage source currents
    I_src_v = np.zeros(n, dtype=np.complex128)
    I_src_v[idx_src_v] = sol[n_f+n_v+n_src_c:n_f+n_v+n_src_c+n_src_v]

    return I_f_all, V_v_all, I_src_c, I_src_v


def get_current_density(n, d, A_incidence, I_f_all):
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

    # project the face currents into the voxels (0.5 because a current is going in and out)
    I_x = 0.5*np.abs(A_incidence[:, 0:n])*I_f_all[0:n]
    I_y = 0.5*np.abs(A_incidence[:, n:2*n])*I_f_all[n:2*n]
    I_z = 0.5*np.abs(A_incidence[:, 2*n:3*n])*I_f_all[2*n:3*n]

    # convert currents into current densities
    J_x = I_x/(dy*dz)
    J_y = I_y/(dx*dz)
    J_z = I_z/(dx*dy)

    # assemble voxel current densities
    J_v_all = np.stack((J_x, J_y, J_z), axis=1, dtype=np.complex128)

    return J_v_all


def get_assign_field(idx_v, V_v_all, J_v_all):
    """
    Only keep the value of the non-empty voxels (for the potential and current density).
    """

    # flag empty voxels
    V_v = V_v_all[idx_v]
    J_v = J_v_all[idx_v, :]

    return V_v, J_v


def get_terminal(source_idx, V_v_all, I_src_c, I_src_v):
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
                I_tmp = np.complex128(np.sum(I_src_c[idx]))
            elif source_type == "voltage":
                I_tmp = np.complex128(np.sum(I_src_v[idx]))
            else:
                raise ValueError("invalid terminal type")

        # assign the current and voltage
        terminal[tag] = {"V": V_tmp, "I": I_tmp}

        # display
        V_str = "%.3e + %.3ej" % (V_tmp.real, V_tmp.imag)
        I_str = "%.3e + %.3ej" % (I_tmp.real, I_tmp.imag)
        logger.info("terminal: %s : V = %s V : I = %s A" % (tag, V_str, I_str))

    return terminal
