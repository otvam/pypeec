"""
Different functions for extracting the fields and terminal currents and voltages from the solution vector.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np


def get_sol_extract(n, idx_f, idx_v, idx_src_c, idx_src_v, sol):
    """
    Extract the dace currents, voxel potentials, and voltage source currents.

    The problem contains n_v non-empty voxels and n_f internal faces.
    The problem contains n_src_v voltage source voxels.

    The solution vector is set in the following order:
    - n_f: face currents
    - n_v: voxel potentials
    - n_src_v: voltage source currents
    """

    # extract the voxel data_output
    (nx, ny, nz) = n
    n_v = len(idx_v)
    n_f = len(idx_f)
    n_src_c = len(idx_src_c)
    n_src_v = len(idx_src_v)
    n = nx*ny*nz

    # assign face currents
    I_face = np.zeros(3*n, dtype=np.complex128)
    I_face[idx_f] = sol[0:n_f]

    # assign voxel voltages
    V_voxel = np.zeros(n, dtype=np.complex128)
    V_voxel[idx_v] = sol[n_f:n_f+n_v]

    # assign current source currents
    I_src_c = np.zeros(n, dtype=np.complex128)
    I_src_c[idx_src_c] = sol[n_f+n_v:n_f+n_v+n_src_c]

    # assign voltage source currents
    I_src_v = np.zeros(n, dtype=np.complex128)
    I_src_v[idx_src_v] = sol[n_f+n_v+n_src_c:n_f+n_v+n_src_c+n_src_v]

    return I_face, V_voxel, I_src_c, I_src_v


def get_current_density(n, d, A_incidence, I_face):
    """
    Get the voxel current densities from the face currents.
    Combine the currents of all the internal faces of a voxel into a single vector.
    Scale the currents into current densities.
    """

    # extract the voxel data_output
    (nx, ny, nz) = n
    (dx, dy, dz) = d
    n = nx*ny*nz

    # project the face currents into the voxels (0.5 because a current is going in and out)
    I_x = 0.5 * np.abs(A_incidence[:, 0:n]) * I_face[0:n]
    I_y = 0.5 * np.abs(A_incidence[:, n:2*n]) * I_face[n:2*n]
    I_z = 0.5 * np.abs(A_incidence[:, 2*n:3*n]) * I_face[2*n:3*n]

    # convert currents into current densities
    J_x = I_x/(dy*dz)
    J_y = I_y/(dx*dz)
    J_z = I_z/(dx*dy)

    # assemble voxel current densities
    J_voxel = np.stack((J_x, J_y, J_z), axis=1, dtype=np.complex128)

    return J_voxel


def get_assign_field(n, idx_v, V_voxel, J_voxel):
    """
    Assign invalid values to the empty voxels.
    """

    # extract the voxel data_output
    (nx, ny, nz) = n
    n = nx*ny*nz

    # find the indices of the empty voxels
    idx_all = np.arange(n, dtype=np.int64)
    idx_nan = np.setdiff1d(idx_all, idx_v)

    # flag empty voxels
    V_voxel[idx_nan] = np.nan + 1j * np.nan
    J_voxel[idx_nan, :] = np.nan + 1j * np.nan

    return V_voxel, J_voxel


def get_terminal(source, V_voxel, I_src_c, I_src_v):
    """
    Parse the terminal voltages and currents for the sources.
    Assign the results to a dict.
    """

    # init terminal dict
    terminal = dict()

    # parse the current source terminals
    for tag, dat_tmp in source.items():
        # get the data
        source_type = dat_tmp["source_type"]
        idx = dat_tmp["idx"]

        # append the source
        if len(idx) == 0:
            I_tmp = np.nan
            V_tmp = np.nan
        else:
            # voltage is the average between all the voxels composing the terminal
            V_tmp = np.complex128(np.mean(V_voxel[idx]))

            # current is the sum between all the voxels composing the terminal
            if source_type == "current":
                I_tmp = np.complex128(np.sum(I_src_c[idx]))
            elif source_type == "voltage":
                I_tmp = np.complex128(np.sum(I_src_v[idx]))
            else:
                raise ValueError("invalid terminal type")

        # assign the current and voltage
        terminal[tag] = {"V": V_tmp, "I": I_tmp}

    return terminal
