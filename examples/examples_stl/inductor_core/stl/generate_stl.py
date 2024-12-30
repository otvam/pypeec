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
    coil = coil.moveTo(+26.0, +1.0).rect(10.0, 44.0).extrude(1.0)
    coil = coil.moveTo(0.0, -16.0).rect(62.0, 10.0).extrude(1.0)
    coil = coil.moveTo(-26.0, 0.0).rect(10.0, 42.0).extrude(1.0)
    coil = coil.moveTo(-6.5, +16.0).rect(49.0, 10.0).extrude(1.0)

    coil = coil.faces(">Z").workplane()
    coil = coil.moveTo(+13.0, +16.0).rect(10.0, 10.0).extrude(1.0)

    coil = coil.faces(">Z").workplane()
    coil = coil.moveTo(+19.5, +16.0).rect(23.0, 10.0).extrude(1.0)
    coil = coil.moveTo(+26.0, 0.0).rect(10.0, 42.0).extrude(1.0)
    coil = coil.moveTo(0.0, -16.0).rect(62.0, 10.0).extrude(1.0)
    coil = coil.moveTo(-26.0, 0.0).rect(10.0, 42.0).extrude(1.0)
    coil = coil.moveTo(-13.0, +16.0).rect(36.0, 10.0).extrude(1.0)

    coil = coil.faces(">Z").workplane()
    coil = coil.moveTo(0.0, +16.0).rect(10.0, 10.0).extrude(1.0)

    coil = coil.faces(">Z").workplane()
    coil = coil.moveTo(+13.0, +16.0).rect(36.0, 10.0).extrude(1.0)
    coil = coil.moveTo(+26.0, 0.0).rect(10.0, 42.0).extrude(1.0)
    coil = coil.moveTo(0.0, -16.0).rect(62.0, 10.0).extrude(1.0)
    coil = coil.moveTo(-26.0, 0.0).rect(10.0, 42.0).extrude(1.0)
    coil = coil.moveTo(-19.5, +16.0).rect(23.0, 10.0).extrude(1.0)

    coil = coil.faces(">Z").workplane()
    coil = coil.moveTo(-13.0, +16.0).rect(10.0, 10.0).extrude(1.0)

    coil = coil.faces(">Z").workplane()
    coil = coil.moveTo(+6.5, +16.0).rect(49.0, 10.0).extrude(1.0)
    coil = coil.moveTo(+26.0, 0.0).rect(10.0, 42.0).extrude(1.0)
    coil = coil.moveTo(0.0, -16.0).rect(62.0, 10.0).extrude(1.0)
    coil = coil.moveTo(-26.0, +1.0).rect(10.0, 44.0).extrude(1.0)

    coil = coil.faces("<Z").workplane()
    coil = coil.moveTo(+26.0, -23.5).rect(10.0, 1.0).extrude(-1.0)
    coil = coil.moveTo(-26.0, -23.5).rect(10.0, 1.0).extrude(-1.0)
    coil = coil.moveTo(-26.0, -22.5).rect(10.0, 1.0).extrude(-7.0)

    core = cq.Workplane("XZ")
    core = core.moveTo(0.0, +3.5).box(80.0, 21.0, 18.0)
    core = core.moveTo(+26.0, +3.5).rect(14.0, 11.0).cutThruAll()
    core = core.moveTo(-26.0, +3.5).rect(14.0, 11.0).cutThruAll()

    src = cq.Workplane("XY").moveTo(-26.0, +24.5).rect(10.0, 1.0).extrude(1.0)
    sink = cq.Workplane("XY").moveTo(+26.0, +24.5).rect(10.0, 1.0).extrude(1.0)

    cad_dict = {
        "coil": coil,
        "core": core,
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
