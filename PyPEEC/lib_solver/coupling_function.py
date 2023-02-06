"""
Different functions for computing coupling functions between voxels.
Analytical solutions and numerical approximations are used.

Exact Inductance Equations for Rectangular Conductors With Applications to More Complicated Geometries
C. Hoer and C. Love, 1965

Exact Closed Form Formula for Self Inductance of Conductor of Rectangular Cross Section
Z. Piatek and B. Baron, 2021
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np
import numpy.linalg as lna


def _get_safe_inv(x):
    """
    Compute the inverse. Set to zero if not finite.
    """

    y = 1/x
    y[np.isnan(y)] = 0.0
    y[np.isinf(y)] = 0.0

    return y


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


def _get_coupling_fct(x, y, z):
    """
    Compute part of the analytical coupling function between two voxels.
    The analytical solution for points is computed for a given distances.
    """

    # precompute terms
    with np.errstate(all="ignore"):
        nrm = np.sqrt(x**2+y**2+z**2)
        inv = _get_safe_inv(nrm)
        invx = _get_safe_inv(x+nrm)
        invy = _get_safe_inv(y+nrm)
        invxz = _get_safe_inv(x**2+z**2)
        invyz = _get_safe_inv(y**2+z**2)
        invxyz = _get_safe_inv(x**2*y**2+x**2*z**2+y**2*z**2+z**4)
        logx = _get_safe_log(x+nrm)
        logy = _get_safe_log(y+nrm)
        logz = _get_safe_log(z+nrm)
        atany = _get_safe_arctan((x*z)/(y*nrm))
        atanx = _get_safe_arctan((y*z)/(x*nrm))
        atanz = _get_safe_arctan((x*y)/(z*nrm))

    # compute function
    val = 1.0*(
            +(z**3*nrm)/15 +
            + (z**5*inv)/60+
            - (x**4*logz)/24 +
            - (y**4*logz)/24 +
            - (x*z**3*logx)/6 +
            - (y*z**3*logy)/6 +
            + (x**2*y**2*logz)/4 +
            + (x*y**2*z*logx)/2 +
            + (x**2*y*z*logy)/2 +
            - (x*y**3*atany)/6 +
            - (x**3*y*atanx)/6 +
            - (x*y*z**2*atanz)/2 +
            - (x**2*z**3*inv)/20 +
            - (y**2*z**3*inv)/20 +
            - (x**2*z*nrm)/10 +
            - (y**2*z*nrm)/10 +
            - (x**4*z*inv)/40 +
            - (y**4*z*inv)/40 +
            + (x**2*y**2*z*inv)/5 +
            - (x*z**5*inv*invx)/24 +
            - (y*z**5*inv*invy)/24 +
            - (x**4*y**2*z*inv*invxz)/(6) +
            - (x**2*y**4*z*inv*invyz)/(6) +
            + (x*y**2*z**3*inv*invx)/4 +
            + (x**2*y*z**3*inv*invy)/4 +
            - (x*y**4*z*inv*invx)/24 +
            - (x**4*y*z*inv*invy)/24 +
            + (x**2*y**2*z**5*inv*invxyz)/3 +
            + (x**2*y**4*z**3*inv*invxyz)/6 +
            + (x**4*y**2*z**3*inv*invxyz)/6
    )

    return val


def _get_coupling_preproc():
    """
    Compute part of the analytical coupling function between two voxels.
    Offset vectors, which are used to compute the distances between points, are generated.
    A sign vector, which is used to sum the points, id generated.
    """

    # get the offset vector
    offset_xy = np.array([-1.0, 0.0, +1.0, 0.0], dtype=np.float64)
    offset_z = np.array([+0.5, -0.5], dtype=np.float64)
    (offset_x, offset_y, offset_z) = np.meshgrid(offset_xy, offset_xy, offset_z)
    offset_x = offset_x.flatten()
    offset_y = offset_y.flatten()
    offset_z = offset_z.flatten()

    # get the sign indices
    idx_xy = np.arange(1, 5, dtype=np.int64)
    idx_z = np.arange(1, 3, dtype=np.int64)
    (idx_x, idx_y, idx_z) = np.meshgrid(idx_xy, idx_xy, idx_z)
    idx_x = idx_x.flatten()
    idx_y = idx_y.flatten()
    idx_z = idx_z.flatten()

    # get the sign vector
    sign = (-1)**(idx_x+idx_y+idx_z+1)

    return offset_x, offset_y, offset_z, sign


def _get_coupling_ana(d, idx):
    """
    Compute a coupling function between two voxels.
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
    (offset_x, offset_y, offset_z, sign) = _get_coupling_preproc()

    # position vector
    x_vec = dx*(idx_x+offset_x)
    y_vec = dy*(idx_y+offset_y)
    z_vec = dz*(idx_z+offset_z)

    # compute the values
    val = _get_coupling_fct(x_vec, y_vec, z_vec)

    # sum the value of all the points
    G = np.sum(sign*val, axis=1)

    # add scaling
    G = G/(4*np.pi)

    return G


def _get_coupling_num(d, idx):
    """
    Compute a coupling function between two voxels.
    Approximation of the mutual coefficients.
    Only valid for mutual coefficients (and not for the self-coefficient).
    Only valid if the distance between the two voxels is large.
    """

    # extract the voxel data
    (dx, dy, dz) = d

    # compute the volume and the distance
    vol = np.prod(d)

    # compute the physical distance
    dis = lna.norm(np.multiply(d, idx), axis=1)

    # compute the approximation
    G = (dx*dy*vol)/(4*np.pi*dis)

    return G


def _get_coupling(d, idx, method, dimension):
    """
    Compute a coupling function between two voxels.
    An analytical solution is used.
    If the distance between the voxels is zero, the self-coefficient is computed.
    """

    # extract the voxel data
    (dx, dy, dz) = d
    d = np.array(d, np.float64)

    # dimension permutation
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
    idx_add = np.array([[0, 0, 0.5]])

    # get the partially integrated coefficients
    if method == "ana":
        G_1 = _get_coupling_ana(d_tmp, idx_tmp+idx_add)
        G_2 = _get_coupling_ana(d_tmp, idx_tmp-idx_add)
    elif method == "num":
        G_1 = _get_coupling_num(d_tmp, idx_tmp+idx_add)
        G_2 = _get_coupling_num(d_tmp, idx_tmp-idx_add)
    else:
        raise ValueError("invalid method")

    # scale the coefficients
    if dimension == "xy":
        G = +(G_2-G_1)/(dy*dz*dx*dz)
    elif dimension == "xz":
        G = -(G_2-G_1)/(dy*dz*dx*dy)
    elif dimension == "yz":
        G = +(G_2-G_1)/(dx*dz*dx*dy)
    else:
        raise ValueError("invalid dimension")

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


def get_coupling_tensor(n, d, coupling_simplify):
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
    n = nx*ny*nz

    # get the indices of the complete voxel structure (as a matrix)
    idx = _get_voxel_indices(nx, ny, nz)

    # compute the normalized distance between the voxels and the reference voxel at the origin
    n_cell = lna.norm(idx, axis=1)

    # check where the analytical solution should be used
    idx_ana = n_cell <= coupling_simplify
    idx_num = np.invert(idx_ana)

    # init the result vector
    K_mutual = np.zeros((n, 3), dtype=np.float64)

    # analytical solution
    K_mutual[idx_ana, 0] = _get_coupling(d, idx[idx_ana], "ana", "yz")
    K_mutual[idx_ana, 1] = _get_coupling(d, idx[idx_ana], "ana", "xz")
    K_mutual[idx_ana, 2] = _get_coupling(d, idx[idx_ana], "ana", "xy")

    # numerical solution
    K_mutual[idx_num, 0] = _get_coupling(d, idx[idx_num], "num", "yz")
    K_mutual[idx_num, 1] = _get_coupling(d, idx[idx_num], "num", "xz")
    K_mutual[idx_num, 2] = _get_coupling(d, idx[idx_num], "num", "xy")

    # transform the vector into a tensor
    K_mutual = K_mutual.flatten(order="F")
    K_mutual = K_mutual.reshape((nx, ny, nz, 3), order="F")

    return K_mutual
