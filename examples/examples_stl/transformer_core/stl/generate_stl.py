"""
Build the CAD objects and export STL files.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import sys
import cadquery as cq


def get_cad():
    """
    Get the different CAD objects.
    """

    coil = cq.Workplane("XY", origin=(0.0, 0.0, -2.5))
    coil = coil.moveTo(+14.0, +2.0).rect(10.0, 46.0).extrude(1.0)
    coil = coil.moveTo(0.0, -16.0).rect(38.0, 10.0).extrude(1.0)
    coil = coil.moveTo(-14.0, 0.0).rect(10.0, 42.0).extrude(1.0)
    coil = coil.moveTo(-6.0, +16.0).rect(26.0, 10.0).extrude(1.0)

    coil = coil.faces(">Z").workplane()
    coil = coil.moveTo(+4.0, +16.0).rect(6.0, 10.0).extrude(1.0)

    coil = coil.faces(">Z").workplane()
    coil = coil.moveTo(+10.0, +16.0).rect(18.0, 10.0).extrude(1.0)
    coil = coil.moveTo(+14.0, 0.0).rect(10.0, 42.0).extrude(1.0)
    coil = coil.moveTo(0.0, -16.0).rect(38.0, 10.0).extrude(1.0)
    coil = coil.moveTo(-14.0, 0.0).rect(10.0, 42.0).extrude(1.0)
    coil = coil.moveTo(-10.0, +16.0).rect(18.0, 10.0).extrude(1.0)

    coil = coil.faces(">Z").workplane()
    coil = coil.moveTo(-4.0, +16.0).rect(6.0, 10.0).extrude(1.0)

    coil = coil.faces(">Z").workplane()
    coil = coil.moveTo(+6.0, +16.0).rect(26.0, 10.0).extrude(1.0)
    coil = coil.moveTo(+14.0, 0.0).rect(10.0, 42.0).extrude(1.0)
    coil = coil.moveTo(0.0, -16.0).rect(38.0, 10.0).extrude(1.0)
    coil = coil.moveTo(-14.0, +2.0).rect(10.0, 46.0).extrude(1.0)

    core = cq.Workplane("XZ")
    core = core.moveTo(0.0, 0.0).box(52.0, 19.0, 16.0)
    core = core.moveTo(0.0, 0.0).rect(28.0, 9.0).cutThruAll()

    src = cq.Workplane("XY").moveTo(+14.0, +25.5).rect(10.0, 1.0).extrude(1.0)
    sink = cq.Workplane("XY").moveTo(-14.0, +25.5).rect(10.0, 1.0).extrude(1.0)
    src = src.translate((0.0, 0.0, -2.5))
    sink = sink.translate((0.0, 0.0, +1.5))

    cad_dict = {
        "core": core,
        "pri_coil": coil.translate((+20.0, 0.0, 0.0)),
        "pri_src": src.translate((+20.0, 0.0, 0.0)),
        "pri_sink": sink.translate((+20.0, 0.0, 0.0)),
        "sec_coil": coil.mirror(mirrorPlane="XY").translate((-20.0, 0.0, 0.0)),
        "sec_src": src.mirror(mirrorPlane="XY").translate((-20.0, 0.0, 0.0)),
        "sec_sink": sink.mirror(mirrorPlane="XY").translate((-20.0, 0.0, 0.0)),
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

    # exit
    sys.exit(0)
