"""
Different functions for computing Green functions with voxels.
Analytical solutions and numerical approximations are used.

The following integral is computed:
    - g(r, r') = 1/|r-r'|
    - G = int g(r, r') dV dV'
    - g(x, y, z, x', y', z') = 1/sqrt((x-x')^2+(y-y')^2+(z-z')^2)
    - G = int g(x, y, z, x', y', z') dx dy dz dx' dy' dz'

Exact Inductance Equations for Rectangular Conductors With Applications to More Complicated Geometries
C. Hoer and C. Love, 1965

Exact Closed Form Formula for Self Inductance of Conductor of Rectangular Cross Section
Z. Piatek and B. Baron, 2021
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
    y[np.isnan(y)] = 0.0
    y[np.isinf(y)] = 0.0

    return y


def _get_safe_arctan(x):
    """
    Compute the arctan. Set to zero if not finite.
    """

    y = np.arctan(x)
    y[np.isnan(y)] = 0.0
    y[np.isinf(y)] = 0.0

    return y


def _get_green_fct(x, y, z):
    """
    Compute part of the analytical Green function between two voxels.
    The analytical solution for points is computed for a given distances.
    """

    # precompute terms
    nrm = np.sqrt(x**2+y**2+z**2)
    atanx = _get_safe_arctan((y*z)/(x*nrm))
    atany = _get_safe_arctan((x*z)/(y*nrm))
    atanz = _get_safe_arctan((x*y)/(z*nrm))
    logx = _get_safe_log(x+nrm)
    logy = _get_safe_log(y+nrm)
    logz = _get_safe_log(z+nrm)

    # compute function
    val = 1.0*(
            +(x**4*nrm)/60 +
            + (y**4*nrm)/60 +
            + (z**4*nrm)/60 +
            - (x*y**4*logx)/24 +
            - (x*z**4*logx)/24 +
            - (x**4*y*logy)/24 +
            - (y*z**4*logy)/24 +
            - (x**4*z*logz)/24 +
            - (y**4*z*logz)/24 +
            - (x**2*y**2*nrm)/20 +
            - (x**2*z**2*nrm)/20 +
            - (y**2*z**2*nrm)/20 +
            + (x*y**2*z**2*logx)/4 +
            + (x**2*y*z**2*logy)/4 +
            + (x**2*y**2*z*logz)/4 +
            - (x*y*z**3*atanz)/6 +
            - (x*y**3*z*atany)/6 +
            - (x**3*y*z*atanx)/6
    )

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


def _get_green_ana(d, idx):
    """
    Compute a Green function between two voxels.
    An analytical solution is used.
    If the distance between the voxels is zero, the self-coefficient is computed.
    """

    # extract the voxel data
    (dx, dy, dz) = d

    # extract the voxel distance
    idx_x = idx[:, [0]]
    idx_y = idx[:, [1]]
    idx_z = idx[:, [2]]

    # get the offset and sign vectors
    (offset_x, offset_y, offset_z, sign) = _get_green_preproc()

    # position vector
    x_vec = dx*(idx_x+offset_x)
    y_vec = dy*(idx_y+offset_y)
    z_vec = dz*(idx_z+offset_z)

    # ignore division per zero (as it handled inside the log and arctan)
    with np.errstate(all="ignore"):
        val = _get_green_fct(x_vec, y_vec, z_vec)

    # sum the value of all the points
    G = np.sum(sign*val, axis=1)

    # add scaling
    G = G/(4*np.pi)

    return G


def _get_green_num(d, idx):
    """
    Compute a Green function between two voxels.
    Approximation of the mutual coefficients.
    Only valid for mutual coefficients (and not for the self-coefficient).
    Only valid if the distance between the two voxels is large.
    """

    # compute the volume and the distance
    vol = np.prod(d)

    # compute the physical distance
    dis = lna.norm(np.multiply(d, idx), axis=1)

    # compute the approximation
    G = (vol*vol)/(4*np.pi*dis)

    return G


def _get_voxel_indices(nx, ny, nz):
    """
    Compute the indices of the complete voxel structure.
    Return the indices as a matrix.
    """

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


def get_green_self(d):
    """
    Compute the self-coefficient for the Green functions.
    The self-coefficient is used for the preconditioner.
    """

    m = np.array([[0, 0, 0]], dtype=np.int64)
    G_self = _get_green_ana(d, m)

    return G_self


def get_green_tensor(n, d, green_simplify):
    """
    Compute the Green functions for the complete voxel structure.
    For the self-coefficient and the close mutual coefficients, an analytical solution is used.
    For the remote mutual coefficients, an approximation is used.

    The voxel structure has the following size: (nx, ny, nz).
    The created tensor has the following dimension: (nx, ny, nz).
    The self-coefficient is at the following location: (0, 0, 0).
    All the elements are computed with respect to the first voxel.
    """

    # extract the voxel data
    (nx, ny, nz) = n
    n = nx*ny*nz

    # get the indices of the complete voxel structure (as a matrix)
    idx = _get_voxel_indices(nx, ny, nz)

    # compute the normalized distance between the voxels and the reference voxel at the origin
    n_cell = lna.norm(idx, axis=1)

    # check where the analytical solution should be used
    idx_ana = n_cell <= green_simplify
    idx_num = np.invert(idx_ana)

    # init the result vector
    G_mutual = np.zeros(n, dtype=np.float64)

    # analytical solution
    G_mutual[idx_ana] = _get_green_ana(d, idx[idx_ana])

    # numerical solution
    G_mutual[idx_num] = _get_green_num(d, idx[idx_num])

    # transform the vector into a tensor
    G_mutual = G_mutual.reshape((nx, ny, nz), order="F")

    return G_mutual
