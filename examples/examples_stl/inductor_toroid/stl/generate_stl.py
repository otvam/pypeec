"""
Build the CAD objects and export STL files.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import cadquery as cq


def get_cad():
    """
    Get the different CAD objects.
    """

    core = cq.Workplane("XY").cylinder(height=8.0, radius=16.0)
    core = core.circle(10.0).cutThruAll()

    coil = cq.Workplane("XZ").moveTo(+13, 0.0).box(20.0, 20.0, 8.0)
    coil = coil.moveTo(+13, 0).rect(12.0, 12.0).cutThruAll()
    coil = coil.moveTo(+21, 0).rect(4.0, 4.0).cutThruAll()

    src = cq.Workplane("XZ").moveTo(+21.0, +1.5).box(4.0, 1.0, 8.0)
    sink = cq.Workplane("XZ").moveTo(+21.0, -1.5).box(4.0, 1.0, 8.0)

    cad_dict = {
        "core": core,
        "coil": coil,
        "src": src,
        "sink": sink,
    }

    return cad_dict


def write_cad(cad_dict, tol):
    """
    Export CAD objects to STL files.
    """

    for tag, cad in cad_dict.items():
        if cad is not None:
            cad.val().exportStl("%s.stl" % tag, tolerance=tol)


if __name__ == "__main__":
    # get the object tolerance
    tol = 1e-3

    # get the CAD objects
    cad_dict = get_cad()

    # save STL/STEP files
    write_cad(cad_dict, tol)
