"""
Different functions for computing Green functions with voxels.
Analytical solutions and numerical approximations are used.

The two following integrals are available:
    - integrate all the dimensions (6D integrals)
    - integrate the dimensions except the last one (5D integrals)

Exact Inductance Equations for Rectangular Conductors With Applications to More Complicated Geometries
C. Hoer and C. Love, 1965

Exact Closed Form Formula for Self Inductance of Conductor of Rectangular Cross Section
Z. Piatek and B. Baron, 2021
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import scilogger
import numpy as np
import numpy.linalg as lna

# get a logger
LOGGER = scilogger.get_logger(__name__, "pypeec")


def _get_safe_inv(x):
    """
    Compute the inverse. Set to zero if not finite.
    """

    y = 1 / x
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


def _get_green_6D_fct(x, y, z):
    """
    Compute the analytical Green function between two voxels.
    All the dimensions are integrated (6D integrals).
    The analytical solution for points is computed for a given distances.
    """

    # precompute terms
    with np.errstate(all="ignore"):
        nrm = np.sqrt(x**2 + y**2 + z**2)
        atanx = _get_safe_arctan((y * z) / (x * nrm))
        atany = _get_safe_arctan((x * z) / (y * nrm))
        atanz = _get_safe_arctan((x * y) / (z * nrm))
        logx = _get_safe_log(x + nrm)
        logy = _get_safe_log(y + nrm)
        logz = _get_safe_log(z + nrm)

    # compute function
    val = 1.0 * (
        +(x**4 * nrm) / 60
        + +(y**4 * nrm) / 60
        + +(z**4 * nrm) / 60
        + -(x * y**4 * logx) / 24
        + -(x * z**4 * logx) / 24
        + -(x**4 * y * logy) / 24
        + -(y * z**4 * logy) / 24
        + -(x**4 * z * logz) / 24
        + -(y**4 * z * logz) / 24
        + -(x**2 * y**2 * nrm) / 20
        + -(x**2 * z**2 * nrm) / 20
        + -(y**2 * z**2 * nrm) / 20
        + +(x * y**2 * z**2 * logx) / 4
        + +(x**2 * y * z**2 * logy) / 4
        + +(x**2 * y**2 * z * logz) / 4
        + -(x * y * z**3 * atanz) / 6
        + -(x * y**3 * z * atany) / 6
        + -(x**3 * y * z * atanx) / 6
    )

    return val


def _get_green_5D_fct(x, y, z):
    """
    Compute the analytical Green function between two voxels.
    All the dimensions except the last one are integrated (5D integrals).
    The analytical solution for points is computed for a given distances.
    """

    # precompute terms
    with np.errstate(all="ignore"):
        nrm = np.sqrt(x**2 + y**2 + z**2)
        inv = _get_safe_inv(nrm)
        invx = _get_safe_inv(x + nrm)
        invy = _get_safe_inv(y + nrm)
        invxz = _get_safe_inv(x**2 + z**2)
        invyz = _get_safe_inv(y**2 + z**2)
        invxyz = _get_safe_inv(x**2 * y**2 + x**2 * z**2 + y**2 * z**2 + z**4)
        logx = _get_safe_log(x + nrm)
        logy = _get_safe_log(y + nrm)
        logz = _get_safe_log(z + nrm)
        atany = _get_safe_arctan((x * z) / (y * nrm))
        atanx = _get_safe_arctan((y * z) / (x * nrm))
        atanz = _get_safe_arctan((x * y) / (z * nrm))

    # compute function
    val = 1.0 * (
        +(z**3 * nrm) / 15
        + +(z**5 * inv) / 60
        + -(x**4 * logz) / 24
        + -(y**4 * logz) / 24
        + -(x * z**3 * logx) / 6
        + -(y * z**3 * logy) / 6
        + +(x**2 * y**2 * logz) / 4
        + +(x * y**2 * z * logx) / 2
        + +(x**2 * y * z * logy) / 2
        + -(x * y**3 * atany) / 6
        + -(x**3 * y * atanx) / 6
        + -(x * y * z**2 * atanz) / 2
        + -(x**2 * z**3 * inv) / 20
        + -(y**2 * z**3 * inv) / 20
        + -(x**2 * z * nrm) / 10
        + -(y**2 * z * nrm) / 10
        + -(x**4 * z * inv) / 40
        + -(y**4 * z * inv) / 40
        + +(x**2 * y**2 * z * inv) / 5
        + -(x * z**5 * inv * invx) / 24
        + -(y * z**5 * inv * invy) / 24
        + -(x**4 * y**2 * z * inv * invxz) / 6
        + -(x**2 * y**4 * z * inv * invyz) / 6
        + +(x * y**2 * z**3 * inv * invx) / 4
        + +(x**2 * y * z**3 * inv * invy) / 4
        + -(x * y**4 * z * inv * invx) / 24
        + -(x**4 * y * z * inv * invy) / 24
        + +(x**2 * y**2 * z**5 * inv * invxyz) / 3
        + +(x**2 * y**4 * z**3 * inv * invxyz) / 6
        + +(x**4 * y**2 * z**3 * inv * invxyz) / 6
    )

    return val


def _get_green_preproc(int_type):
    """
    Compute the integral boundaries for the Green functions.
    Offset vectors, which are used to compute the distances between points, are generated.
    A sign vector, which is used to sum (integrate) the points, is generated.

    For the 6D integral, 64 boundaries points are generated.
    For the 5D integral, 32 boundaries points are generated.
    """

    # get the offset vector
    if int_type == "6D":
        offset_xy = np.array([-1.0, 0.0, +1.0, 0.0], dtype=np.float64)
        offset_z = np.array([-1.0, 0.0, +1.0, 0.0], dtype=np.float64)
        idx_xy = np.arange(1, 5, dtype=np.int64)
        idx_z = np.arange(1, 5, dtype=np.int64)
    elif int_type == "5D":
        offset_xy = np.array([-1.0, 0.0, +1.0, 0.0], dtype=np.float64)
        offset_z = np.array([+0.5, -0.5], dtype=np.float64)
        idx_xy = np.arange(1, 5, dtype=np.int64)
        idx_z = np.arange(1, 3, dtype=np.int64)
    else:
        raise ValueError("invalid integral type")

    (offset_x, offset_y, offset_z) = np.meshgrid(offset_xy, offset_xy, offset_z)
    offset_x = offset_x.flatten()
    offset_y = offset_y.flatten()
    offset_z = offset_z.flatten()

    # get the sign indices
    (idx_x, idx_y, idx_z) = np.meshgrid(idx_xy, idx_xy, idx_z)
    idx_x = idx_x.flatten()
    idx_y = idx_y.flatten()
    idx_z = idx_z.flatten()

    # get the sign vector
    sign = (-1) ** (idx_x + idx_y + idx_z + 1)

    return offset_x, offset_y, offset_z, sign


def get_green_ana(d, idx, int_type):
    """
    Compute a Green function between two voxels.
    An analytical solution is used.
    The 5D or 6D integrals can be computed.
    """

    # check if empty
    if len(idx) == 0:
        return np.empty(0, dtype=np.float64)

    # display
    LOGGER.debug("analytical solution: %s / %d" % (int_type, len(idx)))

    # extract the voxel data
    (dx, dy, dz) = d

    # extract the voxel distance
    idx_x = idx[:, [0]]
    idx_y = idx[:, [1]]
    idx_z = idx[:, [2]]

    # get the offset and sign vectors
    (offset_x, offset_y, offset_z, sign) = _get_green_preproc(int_type)

    # position vector
    x_vec = dx * (idx_x + offset_x)
    y_vec = dy * (idx_y + offset_y)
    z_vec = dz * (idx_z + offset_z)

    # compute the values
    if int_type == "6D":
        val = _get_green_6D_fct(x_vec, y_vec, z_vec)
    elif int_type == "5D":
        val = _get_green_5D_fct(x_vec, y_vec, z_vec)
    else:
        raise ValueError("invalid integral type")

    # sum the value of all the points
    G = np.sum(sign * val, axis=1)

    # add scaling
    G = G / (4 * np.pi)

    return G


def get_green_num(d, idx, int_type):
    """
    Compute a Green function between two voxels.
    The 5D or 6D integrals can be computed.
    A numerical approximation is used.
    Only valid if the distance between the two voxels is large.
    """

    # check if empty
    if len(idx) == 0:
        return np.empty(0, dtype=np.float64)

    # display
    LOGGER.debug("numerical approximation: %s / %d" % (int_type, len(idx)))

    # extract the voxel data
    (dx, dy, dz) = d

    # get the volume
    vol = dx * dy * dz

    # compute the physical distance
    dis = lna.norm(np.multiply(d, idx), axis=1)

    # compute the approximation
    if int_type == "6D":
        G = (vol * vol) / (4 * np.pi * dis)
    elif int_type == "5D":
        G = (dx * dy * vol) / (4 * np.pi * dis)
    else:
        raise ValueError("invalid integral type")

    return G
