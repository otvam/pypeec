"""
Convert voxel indices (linear and tensor indices).
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import sys
from pypeec.utils import voxel


if __name__ == "__main__":
    # ######################## definition of voxel structure size
    n = [5, 5, 7]

    # ######################## dictionary with the voxel indices
    idx_input = {}

    # ######################## definition of conductor indices
    idx_x = 2
    idx_y = 2
    idx_z_min = 0
    idx_z_max = 6

    idx_input["src"] = [[idx_x, idx_y, idx_z_min]]
    idx_input["sink"] = [[idx_x, idx_y, idx_z_max]]

    idx_input["wire"] = []
    for idx_z in range(idx_z_min+1, idx_z_max+0):
        idx_input["wire"].append([idx_x, idx_y, idx_z])

    # ######################## definition of core indices
    idx_xy_min = 0
    idx_xy_max = 4
    idx_z_min = 2
    idx_z_max = 4

    idx_input["core"] = []
    for idx_z in range(idx_z_min+0, idx_z_max+1):
        for idx_x in range(idx_xy_min+0, idx_xy_max+1):
            for idx_y in range(idx_xy_min+0, idx_xy_max+1):
                if (idx_x in [idx_xy_min, idx_xy_max]) or (idx_y in [idx_xy_min, idx_xy_max]):
                    idx_input["core"].append([idx_x, idx_y, idx_z])

    # ######################## converter tensor to linear indices
    idx_linear = {tag: voxel.get_idx_linear(n, idx) for tag, idx in idx_input.items()}

    # ######################## converter linear to tensor indices
    idx_tensor = {tag: voxel.get_idx_tensor(n, idx) for tag, idx in idx_linear.items()}

    # ######################## display the indices
    print("linear indices")
    for tag, idx in idx_linear.items():
        print("    %s = %s" % (tag, idx.tolist()))

    print("tensor indices")
    for tag, idx in idx_tensor.items():
        print("    %s = %s" % (tag, idx.tolist()))

    ii = [
            50, 51, 52, 53, 54, 55, 59, 60, 64, 65, 69, 70, 71, 72, 73, 74, 75,
            76, 77, 78, 79, 80, 84, 85, 89, 90, 94, 95, 96, 97, 98, 99, 100, 101,
            102, 103, 104, 105, 109, 110, 114, 115, 119, 120, 121, 122, 123, 124,
       ]

    # ######################## exit
    sys.exit(0)
