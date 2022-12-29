"""
Different functions for computing Green functions with voxels.
These functions are used during the init phase of the FFT-PEEC method.
"""

import numpy as np

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2022 - Dartmouth College"


def _get_safe_log(x):
    """
    Compute the log. Set to zero if not finite.
    """


    y = np.log(x)
    if not np.isfinite(y):
        y = 0.0

    return y


def _get_safe_arctan(x):
    """
    Compute the arctan. Set to zero if not finite.
    """

    y = np.arctan(x)
    if not np.isfinite(y):
        y = 0.0

    return y


def get_green_ana(d, m):
    """
    Compute a Green function between two voxels.
    Analytical solution (from Cletus Hoer and Carl Love, 1965).
    If the distance between the voxels is zero, the self-coefficient is computed.
    """

    # extract the voxel data
    (mx, my, mz) = m
    (dx, dy, dz) = d

    # analytical solution
    Fn = lambda x, y, z: np.sqrt(x**2+y**2+z**2)
    F1 = lambda x, y, z: +(6/5)*Fn(x, y, z)*(
            +x**4+y**4+z**4 +
            -3*x**2*y**2 +
            -3*x**2*z**2 +
            -3*y**2*z**2
    )
    F2 = lambda x, y, z: 12*x*y*z*(
            -z**2*_get_safe_arctan((x*y)/(z*Fn(x, y, z))) +
            -y**2*_get_safe_arctan((x*z)/(y*Fn(x, y, z))) +
            -x**2*_get_safe_arctan((y*z)/(x*Fn(x, y, z)))
    )
    F3 = lambda x, y, z: 3*(
            -x*(y**4-6*y**2*z**2+z**4)*_get_safe_log(x+Fn(x, y, z)) +
            -y*(x**4-6*x**2*z**2+z**4)*_get_safe_log(y+Fn(x, y, z)) +
            -z*(x**4-6*x**2*y**2+y**4)*_get_safe_log(z+Fn(x, y, z))
    )
    F = lambda x, y, z: (1/72)*(F1(x, y, z)+F2(x, y, z)+F3(x, y, z))

    # position vector
    x = [(mx-1)*dx, mx*dx, (mx+1)*dx, mx*dx]
    y = [(my-1)*dy, my*dy, (my+1)*dy, my*dy]
    z = [(mz-1)*dz, mz*dz, (mz+1)*dz, mz*dz]

    # compute the Green function
    G = 0.0
    for ix in range(4):
        for iy in range(4):
            for iz in range(4):
                with np.errstate(all='ignore'):
                    sign = (-1)**(ix+1+iy+1+iz+1+1)
                    val = F(x[ix], y[iy], z[iz])
                    G += sign*val
    # add scaling
    G = G/(4*np.pi)

    return G


def get_green_center(d, m):
    """
    Compute a Green function between two voxels.
    Approximation of the mutual coefficients.
    Only valid for mutual coefficients (and not for the self-coefficient).
    Only valid if the distance between the voxels is large.
    """

    # compute the volume and the distance
    vol = np.prod(d)
    xyz = np.multiply(d, m)
    nrm = np.linalg.norm(xyz)

    # compute the approximation
    G = (vol*vol)/(4*np.pi*nrm)

    return G


def get_green_tensor(d, n, n_min_center):
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

    # init the tensor
    G_mutual = np.zeros((nx, ny, nz), dtype=np.float64)

    # populate the tensor
    for ix in range(nx):
        for iy in range(ny):
            for iz in range(nz):
                m = [ix, iy, iz]
                n_center = np.linalg.norm(m)

                if n_center<=n_min_center:
                    G_mutual[ix, iy, iz] = get_green_ana(d, m)
                else:
                    G_mutual[ix, iy, iz] = get_green_center(d, m)

    # get the self-coefficient (used for the preconditioner)
    G_self = get_green_ana(d, [0, 0, 0])

    return G_mutual, G_self
