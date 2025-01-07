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

    coil = cq.Workplane("XY").box(80.0, 40, 1.0)
    coil = coil.rect(+72.0, +32.0).cutThruAll()
    coil = coil.moveTo(+48.0, +4.0).box(16.0, 4.0, 1.0)
    coil = coil.moveTo(+48.0, -4.0).box(16.0, 4.0, 1.0)
    coil = coil.moveTo(+38.0, 0.0).rect(4.0, 4.0).cutThruAll()

    src = cq.Workplane("XY").moveTo(+56.5, +4.0).box(1.0, 4.0, 1.0)
    sink = cq.Workplane("XY").moveTo(+56.5, -4.0).box(1.0, 4.0, 1.0)

    cad_dict = {
        "pri_coil": coil.translate((0.0, 0.0, +2.0)),
        "pri_src": src.translate((0.0, 0.0, +2.0)),
        "pri_sink": sink.translate((0.0, 0.0, +2.0)),
        "sec_coil": coil.translate((0.0, 0.0, -2.0)),
        "sec_src": src.translate((0.0, 0.0, -2.0)),
        "sec_sink": sink.translate((0.0, 0.0, -2.0)),
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
