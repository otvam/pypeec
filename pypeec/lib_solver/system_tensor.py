"""
Get the dense matrices used for the PEEC problem:
    - the integral of the Green functions
    - the cross-coupling functions between the faces
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import numpy as np
import numpy.linalg as lna
from pypeec.lib_matrix import green_function


def _get_coupling(d, idx, method, dimension):
    """
    Compute a coupling function between two voxels for a specified coupling (direction of the faces).
    An analytical solution or a numerical approximation is used.
    """

    # extract the voxel data
    (dx, dy, dz) = d
    d = np.array(d, np.float64)

    # dimension permutation:
    #   - the 5D integral is solved for the xy faces
    #   - other faces are permuted to the xy faces
    if dimension == "xy":
        perm = [0, 1, 2]
    elif dimension == "xz":
        perm = [0, 2, 1]
    elif dimension == "yz":
        perm = [1, 2, 0]
    else:
        raise ValueError("invalid dimension")

    # make the permutation
    d_tmp = d[perm]
    idx_tmp = idx[:, perm]

    # shift for the integration of the last dimension
    idx_add = np.array([[0.0, 0.0, 0.5]])

    # compute the evaluation coordinate
    idx_1 = idx_tmp + idx_add
    idx_2 = idx_tmp - idx_add

    # get the partially integrated coefficients (5D integration)
    if method == "ana":
        G_1 = green_function.get_green_ana(d_tmp, idx_1, "5D")
        G_2 = green_function.get_green_ana(d_tmp, idx_2, "5D")
    elif method == "num":
        G_1 = green_function.get_green_num(d_tmp, idx_1, "5D")
        G_2 = green_function.get_green_num(d_tmp, idx_2, "5D")
    else:
        raise ValueError("invalid method")

    # get the 6D integral from the 5D integrals
    #   - the last dimension is the integral of the derivative
    #   - therefore, the integral is reduced to a subtraction
    G = G_2 - G_1

    # scale the coefficients with the area of the faces
    if dimension == "xy":
        G = +G / (dy * dz * dx * dz)
    elif dimension == "xz":
        G = -G / (dy * dz * dx * dy)
    elif dimension == "yz":
        G = +G / (dx * dz * dx * dy)
    else:
        raise ValueError("invalid dimension")

    return G


def _get_voxel_indices(n):
    """
    Compute the indices of the complete voxel structure.
    Return the indices as a matrix.
    """

    # extract the voxel data
    (nx, ny, nz) = n

    # get the indices array
    idx_x = np.arange(nx, dtype=np.int64)
    idx_y = np.arange(ny, dtype=np.int64)
    idx_z = np.arange(nz, dtype=np.int64)
    [idx_x, idx_y, idx_z] = np.meshgrid(idx_x, idx_y, idx_z, indexing="ij")

    # flatten the indices into vectors
    idx_x = idx_x.flatten(order="F")
    idx_y = idx_y.flatten(order="F")
    idx_z = idx_z.flatten(order="F")

    # assemble the vectors in a matrix
    idx = np.stack((idx_x, idx_y, idx_z), axis=1)

    return idx


def _get_voxel_distances(d, idx):
    """
    Compute the normalized distance between the voxels and the reference voxel at the origin.
    """

    # scale the distances
    d_idx = d * idx

    # compute the distances
    d_cell = lna.norm(d_idx, axis=1)

    # normalize the distances
    n_cell = d_cell / max(d)

    return n_cell


def get_green_self(d):
    """
    Compute the self-coefficient for the Green functions.
    The self-coefficient is used for the preconditioner.
    """

    idx = np.array([[0, 0, 0]], dtype=np.int64)
    G_self = green_function.get_green_ana(d, idx, "6D")
    G_self = G_self[0]

    return G_self


def get_green_tensor(n, d, integral_simplify):
    """
    Compute the Green functions for the complete voxel structure.
    For the self-coefficient and the close mutual coefficients, an analytical solution is used.
    For the remote mutual coefficients, an approximation is used.

    The voxel structure has the following size: (nx, ny, nz).
    The created tensor has the following dimension: (nx, ny, nz, 1).
    The self-coefficient is at the following location: (0, 0, 0, 0).
    All the elements are computed with respect to the first voxel.
    """

    # extract the voxel data
    (nx, ny, nz) = n

    # get total size
    nv = np.prod(n)

    # get the indices of the complete voxel structure (as a matrix)
    idx = _get_voxel_indices(n)

    # compute the normalized distance between the voxels and the reference voxel at the origin
    n_cell = _get_voxel_distances(d, idx)

    # check where the analytical solution should be used
    idx_ana = n_cell <= integral_simplify
    idx_num = np.invert(idx_ana)

    # init the result vector
    G_mutual = np.empty(nv, dtype=np.float64)

    # analytical solution
    G_mutual[idx_ana] = green_function.get_green_ana(d, idx[idx_ana], "6D")

    # numerical solution
    G_mutual[idx_num] = green_function.get_green_num(d, idx[idx_num], "6D")

    # transform the vector into a tensor
    G_mutual = G_mutual.reshape((nx, ny, nz, 1), order="F")

    return G_mutual


def get_coupling_tensor(n, d, integral_simplify, has_magnetic):
    """
    Compute the coupling functions for the complete voxel structure.
    For the close coefficients, an analytical solution is used.
    For the remote coefficients, an approximation is used.

    The voxel structure has the following size: (nx, ny, nz).
    The created tensor has the following dimension: (nx, ny, nz, 3).
    All the elements are computed with respect to the first voxel.
    """

    # extract the voxel data
    (nx, ny, nz) = n

    # get total size
    nv = np.prod(n)

    # check if the tensor is required
    if not has_magnetic:
        return None

    # get the indices of the complete voxel structure (as a matrix)
    idx = _get_voxel_indices(n)

    # compute the normalized distance between the voxels and the reference voxel at the origin
    n_cell = _get_voxel_distances(d, idx)

    # check where the analytical solution should be used
    idx_ana = n_cell <= integral_simplify
    idx_num = np.invert(idx_ana)

    # init the result vector
    K_tsr = np.empty((nv, 3), dtype=np.float64)

    # analytical solution
    K_tsr[idx_ana, 0] = _get_coupling(d, idx[idx_ana], "ana", "yz")
    K_tsr[idx_ana, 1] = _get_coupling(d, idx[idx_ana], "ana", "xz")
    K_tsr[idx_ana, 2] = _get_coupling(d, idx[idx_ana], "ana", "xy")

    # numerical solution
    K_tsr[idx_num, 0] = _get_coupling(d, idx[idx_num], "num", "yz")
    K_tsr[idx_num, 1] = _get_coupling(d, idx[idx_num], "num", "xz")
    K_tsr[idx_num, 2] = _get_coupling(d, idx[idx_num], "num", "xy")

    # transform the vector into a tensor
    K_tsr = K_tsr.flatten(order="F")
    K_tsr = K_tsr.reshape((nx, ny, nz, 3), order="F")

    return K_tsr
