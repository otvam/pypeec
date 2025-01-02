"""
Different functions for checking the point cloud.
The point cloud should not intersect with the non-empty voxels.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import scilogger
import numpy as np

# get a logger
LOGGER = scilogger.get_logger(__name__, "pypeec")


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
    o = c - (n * d) / 2

    # assemble the coordinate array
    pts_vox = o + d / 2 + d * idx_vox

    return pts_vox


def _get_point_valid(d, pts_vox, pts_tmp):
    """
    Check if a cloud point is not intersecting with the non-empty voxels.
    """

    # compute distance for each dimension
    pts_dis = np.abs(pts_vox - pts_tmp)
    pts_valid = pts_dis > d

    # check if distance are respected
    pts_valid = np.any(pts_valid, axis=1)

    # valid if all the voxel are valid
    valid = np.all(pts_valid, axis=0)

    return valid


def _get_cloud_valid(c, d, n, domain_def, pts_cloud):
    """
    Check which cloud points are not intersecting with the non-empty voxels.
    """

    # cast to array
    c = np.array(c, dtype=np.float64)
    d = np.array(d, dtype=np.float64)
    n = np.array(n, dtype=np.int64)

    # assemble all the indices
    idx_all = np.empty(0, dtype=np.int64)
    for idx in domain_def.values():
        idx_all = np.append(idx_all, idx)

    # get the voxel coordinate
    pts_vox = _get_voxel_coordinate(n, d, c, idx_all)

    # check the points
    valid_cloud = np.empty(0, dtype=bool)
    for pts_tmp in pts_cloud:
        valid_tmp = _get_point_valid(d, pts_vox, pts_tmp)
        valid_cloud = np.append(valid_cloud, valid_tmp)

    return valid_cloud


def get_point(n, d, c, domain_def, data_point):
    """
    Check that the cloud points are not intersecting with the non-empty voxels.
    """

    # extract the data
    check_cloud = data_point["check_cloud"]
    filter_cloud = data_point["filter_cloud"]
    pts_cloud = data_point["pts_cloud"]

    # display number of cloud points
    LOGGER.debug("check_cloud = %s" % check_cloud)
    LOGGER.debug("filter_cloud = %s" % filter_cloud)
    LOGGER.debug("original number = %d" % len(pts_cloud))

    # cast to array
    pts_cloud = np.array(pts_cloud, np.float64)

    # check valid points
    if check_cloud:
        # get the valid points
        valid_cloud = _get_cloud_valid(c, d, n, domain_def, pts_cloud)

        # remove the invalid points
        if filter_cloud:
            pts_cloud = pts_cloud[valid_cloud]
        else:
            if not np.all(valid_cloud):
                raise RuntimeError("all the cloud points should be located outside the voxel structure")

    # display number of cloud points
    LOGGER.debug("final number = %d" % len(pts_cloud))

    return pts_cloud
