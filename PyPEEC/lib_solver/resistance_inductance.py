"""
Different functions for handling the resistance and inductance matrix.
The resistance matrix is constructed with the non-empty voxels.
The inductance matrix is computed with a FFT circulant tensor.
Thr circulant tensor allows for matrix-vector multiplication with FFT.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np


def get_resistance_vector(n, d, A_reduced, idx_f, rho_v):
    """
    Extract the resistance vector of the system (diagonal of the resistance matrix).

    The problem contains n_f internal faces.
    The resistance vector has the following length: n_f.
    """

    # extract the voxel data
    (nx, ny, nz) = n
    (dx, dy, dz) = d
    n = nx*ny*nz

    # get the resistivity of the faces (average between voxels)
    rho_vector = 0.5*rho_v*np.abs(A_reduced)

    # init the resistance vector
    R_vector = np.zeros(len(rho_vector), dtype=np.float64)

    # get the direction of the faces (x, y, z)
    idx_f_x = np.flatnonzero(np.in1d(idx_f, np.arange(0*n, 1*n)))
    idx_f_y = np.flatnonzero(np.in1d(idx_f, np.arange(1*n, 2*n)))
    idx_f_z = np.flatnonzero(np.in1d(idx_f, np.arange(2*n, 3*n)))

    # resistance vector (different directions)
    R_vector[idx_f_x] = (dx/(dy*dz))*rho_vector[idx_f_x]
    R_vector[idx_f_y] = (dy/(dx*dz))*rho_vector[idx_f_y]
    R_vector[idx_f_z] = (dz/(dx*dy))*rho_vector[idx_f_z]

    return R_vector


def get_inductance_matrix(n, d, idx_f, G_mutual, G_self):
    """
    Extract the inductance matrix of the system.

    The voxel structure has the following size: (nx, ny, nz).
    The problem contains n_f internal faces.
    For solving the full system, an inductance tensor is used: (nx, ny, nz, 3).
    For solving the preconditioner, a vector is used: n_f.
    """

    # extract the voxel data
    (nx, ny, nz) = n
    (dx, dy, dz) = d
    n = nx*ny*nz

    # vacuum permittivity
    mu = 4*np.pi*1e-7

    # compute the inductance tensor from the Green functions
    L_tensor = np.zeros((nx, ny, nz, 3), dtype=np.float64)
    L_tensor[:, :, :, 0] = (mu*G_mutual)/(dy**2*dz**2)
    L_tensor[:, :, :, 1] = (mu*G_mutual)/(dx**2*dz**2)
    L_tensor[:, :, :, 2] = (mu*G_mutual)/(dx**2*dy**2)

    # self-inductance for the preconditioner
    L_x = (mu*G_self)/(dy**2*dz**2)
    L_y = (mu*G_self)/(dx**2*dz**2)
    L_z = (mu*G_self)/(dx**2*dy**2)
    L_vector = np.concatenate((L_x*np.ones(n), L_y*np.ones(n), L_z*np.ones(n)))
    L_vector = L_vector[idx_f]

    return L_tensor, L_vector
