"""
Different functions for checking the point cloud.
The point cloud should not intersect with the non-empty voxels.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import numpy as np
from pypeec import log

# get a logger
LOGGER = log.get_logger(__name__, "pypeec")


def _get_voxel_coordinate(n, d, c, idx_all):
    """
    Get the coordinate of the different voxels.
    The center voxel center is at the specified origin coordinate.
    """

    # convert linear indices into tensor indices
    (idx_x, idx_y, idx_z) = np.unravel_index(idx_all, n, order="F")

    # assemble the coordinate array
    idx_vox = np.stack((idx_x, idx_y, idx_z), axis=1)

    # origin coordinate
    o = c-(n*d)/2

    # assemble the coordinate array
    pts_vox = o+d/2+d*idx_vox

    return pts_vox


def _get_point_valid(d, pts_vox, pts_tmp):
    """
    Check of a cloud point is not intersecting with the non-empty voxels.
    """

    # compute distance for each dimension
    pts_dis = np.abs(pts_vox-pts_tmp)
    pts_valid = pts_dis > d

    # check if distance are respected
    pts_valid = np.any(pts_valid == True, axis=1)
    valid = np.all(pts_valid == True, axis=0)

    return valid


def get_cloud(n, d, c, domain_def, pts_cloud_in):
    """
    Check of the cloud points are not intersecting with the non-empty voxels.
    Keep the valid points, discard the other points.
    """

    # display number of cloud points
    LOGGER.debug("initial number = %d" % len(pts_cloud_in))

    # cast to array
    c = np.array(c, dtype=np.float_)
    d = np.array(d, dtype=np.float_)
    n = np.array(n, dtype=np.int_)

    # assemble all the indices
    idx_all = np.empty(0, dtype=np.int_)
    for idx in domain_def.values():
        idx_all = np.append(idx_all, idx)

    # get the voxel coordinate
    pts_vox = _get_voxel_coordinate(n, d, c, idx_all)

    # check the points
    pts_cloud_out = []
    for pts_tmp in pts_cloud_in:
        valid = _get_point_valid(d, pts_vox, pts_tmp)
        if valid:
            pts_cloud_out.append(pts_tmp)

    # cast
    pts_cloud_out = np.array(pts_cloud_out, np.float_)

    # display number of cloud points
    LOGGER.debug("final number = %d" % len(pts_cloud_out))

    return pts_cloud_out
