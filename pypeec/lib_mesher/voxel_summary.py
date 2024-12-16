"""
Compute and display metrics about 3D voxel structures.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import scilogger

# get a logger
LOGGER = scilogger.get_logger(__name__, "pypeec")


def get_summary(n, d, s, c, pts_cloud, domain_def, graph_def):
    """
    Get a dict summarizing a 3D voxel structure.
    """

    # extract the voxel data
    (nx, ny, nz) = n
    (dx, dy, dz) = d
    (cx, cy, cz) = c
    (sx, sy, sz) = s

    # compute voxel numbers
    n_total = nx * ny * nz
    n_graph = len(graph_def)
    n_domain = len(domain_def)
    n_cloud = len(pts_cloud)

    # get the used voxels
    n_used = sum(len(idx) for idx in domain_def.values())

    # voxel utilization ratio
    ratio = n_used / n_total

    # get the volume and areas
    V_voxel = dx * dy * dz
    V_total = n_total * V_voxel
    V_used = n_used * V_voxel
    A_xy = sx * sy
    A_yz = sy * sz
    A_xz = sx * sz

    # assign data
    voxel_status = {
        "n_total": n_total,
        "n_used": n_used,
        "A_xy": A_xy,
        "A_yz": A_yz,
        "A_xz": A_xz,
        "V_total": V_total,
        "V_used": V_used,
        "ratio": ratio,
        "n_domain": n_domain,
        "n_graph": n_graph,
        "n_cloud": n_cloud,
    }

    # display status
    LOGGER.debug("voxel size")
    with LOGGER.BlockIndent():
        LOGGER.debug("n = (%d, %d, %d)" % (nx, ny, nz))
        LOGGER.debug("d = (%.2e, %.2e, %.2e)" % (dx, dy, dz))
        LOGGER.debug("s = (%.2e, %.2e, %.2e)" % (sx, sy, sz))
        LOGGER.debug("c = (%.2e, %.2e, %.2e)" % (cx, cy, cz))
        LOGGER.debug("A = (%.2e, %.2e, %.2e)" % (A_xy, A_yz, A_xz))

    # plot the voxel number
    LOGGER.debug("voxel summary")
    with LOGGER.BlockIndent():
        LOGGER.debug("V_total = %.2e" % V_total)
        LOGGER.debug("V_used = %.2e" % V_used)
        LOGGER.debug("n_total = %d" % n_total)
        LOGGER.debug("n_used = %d" % n_used)
        LOGGER.debug("ratio = %.2e" % ratio)
        LOGGER.debug("n_domain = %d" % n_domain)
        LOGGER.debug("n_graph = %d" % n_graph)
        LOGGER.debug("n_cloud = %d" % n_cloud)

    # plot the domain size
    LOGGER.debug("voxel domain")
    with LOGGER.BlockIndent():
        for tag, idx in domain_def.items():
            LOGGER.debug("%s = %d" % (tag, len(idx)))

    return voxel_status
