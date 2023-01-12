"""
Different functions for computing Green functions with voxels.
Analytical solutions and numerical approximations are used.
Analytical solution (from Cletus Hoer and Carl Love, 1965).
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np
import numpy.linalg as lna


def _get_safe_log(x):
    """
    Compute the log. Set to zero if not finite.
    """

    y = np.log(x)
    y[np.isnan(y)] = 0
    y[np.isinf(y)] = 0

    return y


def _get_safe_arctan(x):
    """
    Compute the arctan. Set to zero if not finite.
    """

    y = np.arctan(x)
    y[np.isnan(y)] = 0
    y[np.isinf(y)] = 0

    return y


def _get_green_fct(x, y, z):
    """
    Compute part of the analytical Green function between two voxels.
    The analytical solution for points is computed for a given distances.
    """

    nrm = np.sqrt(x**2+y**2+z**2)
    val_1 = (6/5)*nrm*(
            +x**4+y**4+z**4 +
            -3*x**2*y**2 +
            -3*x**2*z**2 +
            -3*y**2*z**2
    )
    val_2 = 12*x*y*z*(
            -z**2*_get_safe_arctan((x*y)/(z*nrm)) +
            -y**2*_get_safe_arctan((x*z)/(y*nrm)) +
            -x**2*_get_safe_arctan((y*z)/(x*nrm))
    )
    val_3 = 3*(
            -x*(y**4-6*y**2*z**2+z**4)*_get_safe_log(x+nrm) +
            -y*(x**4-6*x**2*z**2+z**4)*_get_safe_log(y+nrm) +
            -z*(x**4-6*x**2*y**2+y**4)*_get_safe_log(z+nrm)
    )
    val = (1/72)*(val_1+val_2+val_3)

    return val


def _get_green_preproc():
    """
    Compute part of the analytical Green function between two voxels.
    Offset vectors, which are used to compute the distances between points, are generated.
    A sign vector, which is used to sum the points, id generated.
    """

    # get the offset vector
    offset = np.array([-1, 0, +1, 0], dtype=np.int64)
    (offset_x, offset_y, offset_z) = np.meshgrid(offset, offset, offset)
    offset_x = offset_x.flatten()
    offset_y = offset_y.flatten()
    offset_z = offset_z.flatten()

    # get the sign indices
    idx = np.arange(len(offset), dtype=np.int64)
    (idx_x, idx_y, idx_z) = np.meshgrid(idx, idx, idx)
    idx_x = idx_x.flatten()
    idx_y = idx_y.flatten()
    idx_z = idx_z.flatten()

    # get the sign vector
    sign = (-1)**(idx_x+1+idx_y+1+idx_z+1+1)

    return offset_x, offset_y, offset_z, sign


def _get_green_ana(d, m):
    """
    Compute a Green function between two voxels.
    An analytical solution is used.
    If the distance between the voxels is zero, the self-coefficient is computed.
    """

    # extract the voxel data
    (dx, dy, dz) = d

    # extract the voxel distance
    mx = m[:, [0]]
    my = m[:, [1]]
    mz = m[:, [2]]

    # get the offset and sign vectors
    (offset_x, offset_y, offset_z, sign) = _get_green_preproc()

    # position vector
    x_vec = dx*(mx+offset_x)
    y_vec = dy*(my+offset_y)
    z_vec = dz*(mz+offset_z)

    # ignore division per zero (as it handled inside the log and arctan)
    with np.errstate(all="ignore"):
        val = _get_green_fct(x_vec, y_vec, z_vec)

    # sum the value of all the points
    G = np.sum(sign*val, axis=1)

    # add scaling
    G = G/(4*np.pi)

    return G


def _get_green_num(d, m):
    """
    Compute a Green function between two voxels.
    Approximation of the mutual coefficients.
    Only valid for mutual coefficients (and not for the self-coefficient).
    Only valid if the distance between the two voxels is large.
    """

    # compute the volume and the distance
    vol = np.prod(d)

    # compute the physical distance
    dis = lna.norm(np.multiply(d, m), axis=1)

    # compute the approximation
    G = (vol*vol)/(4*np.pi*dis)

    return G


def _get_voxel_indices(nx, ny, nz):
    """
    Compute the indices of the complete voxel structure.
    Return the indices as a matrix.
    """

    # get the indices array
    mx = np.arange(nx, dtype=np.int64)
    my = np.arange(ny, dtype=np.int64)
    mz = np.arange(nz, dtype=np.int64)
    [mx, my, mz] = np.meshgrid(mx, my, mz, indexing="ij")

    # flatten the indices into vectors
    mx = mx.flatten(order="F")
    my = my.flatten(order="F")
    mz = mz.flatten(order="F")

    # assemble the vectors in a matrix
    m = np.stack((mx, my, mz), axis=1, dtype=np.int64)

    return m


def get_green_self(d):
    """
    Compute the self-coefficient for the Green functions.
    The self-coefficient is used for the preconditioner.
    """

    m = np.array([[0, 0, 0]], dtype=np.int64)
    G_self = _get_green_ana(d, m)

    return G_self


def get_green_tensor(n, d, n_green):
    """
    Compute the Green functions for the complete voxel structure.
    For the self-coefficient and the close mutual coefficients, an analytical solution is used.
    For the remote mutual coefficients, an approximation is used.
    The tensor has the following dimension: (nx, ny, nz).
    The self-coefficient is at the following location: (1,1,1).
    All the elements are computed with respect to the first voxel.
    """

    # extract the voxel data
    (nx, ny, nz) = n
    n = nx*ny*nz

    # get the indices of the complete voxel structure (as a matrix)
    m = _get_voxel_indices(nx, ny, nz)

    # compute the normalized distance between the voxels and the reference voxel at the origin
    n_cell = lna.norm(m, axis=1)

    # check where the analytical solution should be used
    idx_ana = n_cell <= n_green
    idx_num = np.invert(idx_ana)

    # init the result vector
    G_mutual = np.zeros(n, dtype=np.float64)

    # analytical solution
    G_mutual[idx_ana] = _get_green_ana(d, m[idx_ana, :])

    # numerical solution
    G_mutual[idx_num] = _get_green_num(d, m[idx_num, :])

    # transform the vector into a tensor
    G_mutual = G_mutual.reshape((nx, ny, nz), order="F")

    return G_mutual
