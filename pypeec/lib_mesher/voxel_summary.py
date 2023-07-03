"""
Compute and display metrics about 3D voxel structures.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

from pypeec import log

# get a logger
LOGGER = log.get_logger("SUMMARY")


def get_status(n, d, s, c, domain_def, connection_def):
    """
    Get a dict summarizing a 3D voxel structure.
    """

    # extract the voxel data
    (nx, ny, nz) = n
    (dx, dy, dz) = d
    (cx, cy, cz) = c
    (sx, sy, sz) = s

    # compute voxel numbers
    n_total = nx*ny*nz
    n_graph = len(connection_def)
    n_domain = len(domain_def)

    # get the used voxels
    n_used = sum(len(idx) for idx in domain_def.values())

    # voxel utilization ratio
    ratio = n_used/n_total

    # get the volume and areas
    V_voxel = dx*dy*dz
    V_total = n_total*V_voxel
    V_used = n_used*V_voxel
    A_xy = sx*sy
    A_yz = sy*sz
    A_xz = sx*sz

    # assign data
    voxel_status = {
        "n": n,
        "s": s,
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
    }

    # display status
    LOGGER.debug("voxel: number = (nx, ny, nz)) = (%d, %d, %d)" % (nx, ny, nz))
    LOGGER.debug("voxel: size = (dx, dy, dz) =  (%.3e, %.3e, %.3e)" % (dx, dy, dz))
    LOGGER.debug("voxel: span = (sx, sy, sz) =  (%.3e, %.3e, %.3e)" % (sx, sy, sz))
    LOGGER.debug("voxel: center = (cx, cy, cz) =  (%.3e, %.3e, %.3e)" % (cx, cy, cz))

    # plot the voxel number
    LOGGER.debug("size: A_xy = %.3e / A_yz = %.3e / A_xz = %.3e" % (A_xy, A_yz, A_xz))
    LOGGER.debug("size: V_total = %.3e / V_used = %.3e" % (V_total, V_used))
    LOGGER.debug("size: n_total = %d / n_used = %d" % (n_total, n_used))
    LOGGER.debug("size: ratio = %.3e" % ratio)
    LOGGER.debug("size: n_domain = %d" % n_domain)
    LOGGER.debug("size: n_graph = %d" % n_graph)

    # plot the domain size
    for tag, idx in domain_def.items():
        LOGGER.debug("domain: %s = %d" % (tag, len(idx)))

    return voxel_status
