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

    coil = cq.Workplane("XY")
    coil = coil.moveTo(-63.5, +3.0).rect(21.0, 10.0).extrude(5.0)
    coil = coil.moveTo(-58.0, +24).rect(10.0, 52.0).extrude(5.0)
    coil = coil.moveTo(+63.5, +3.0).rect(21.0, 10.0).extrude(5.0)
    coil = coil.moveTo(-6.5, +45.0).rect(113.0, 10.0).extrude(5.0)
    coil = coil.moveTo(+45.0, 0.0).rect(10.0, 100.0).extrude(5.0)
    coil = coil.moveTo(0.0, -45.0).rect(100.0, 10.0).extrude(5.0)
    coil = coil.moveTo(-45.0, -7.0).rect(10.0, 86.0).extrude(5.0)
    coil = coil.moveTo(-7.0, +31.0).rect(86.0, 10.0).extrude(5.0)
    coil = coil.moveTo(+31.0, 0.0).rect(10.0, 72.0).extrude(5.0)
    coil = coil.moveTo(0.0, -31.0).rect(72.0, 10.0).extrude(5.0)
    coil = coil.moveTo(-31.0, -7.0).rect(10.0, 58.0).extrude(5.0)
    coil = coil.moveTo(-7.0, +17.0).rect(58.0, 10.0).extrude(5.0)
    coil = coil.moveTo(+17.0, 0.0).rect(10.0, 44.0).extrude(5.0)
    coil = coil.moveTo(0.0, -17.0).rect(44.0, 10.0).extrude(5.0)
    coil = coil.moveTo(-17.0, -7.0).rect(10.0, 30.0).extrude(5.0)

    coil = coil.faces(">Z").workplane()
    coil = coil.moveTo(-17.0, +3.0).rect(10.0, 10.0).extrude(3.0)
    coil = coil.moveTo(+58.0, +3.0).rect(10.0, 10.0).extrude(3.0)

    coil = coil.faces(">Z").workplane()
    coil = coil.moveTo(+20.5, +3.0).rect(85.0, 10.0).extrude(5.0)

    src = cq.Workplane("XY").moveTo(-74.5, +3.0).rect(1.0, 10.0).extrude(5.0)
    sink = cq.Workplane("XY").moveTo(+74.5, +3.0).rect(1.0, 10.0).extrude(5.0)

    cad_dict = {
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
