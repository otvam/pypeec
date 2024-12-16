"""
Main script for creating a 3D voxel structure.
Check the input data and mesh the structure.
The different parts of the code are timed.

Three different kind of geometry can be meshed:
    - stl: the voxel structure is generated from 3D STL files
    - png: the voxel structure is generated from stacked PNG images
    - shape: the voxel structure is generated from stacked 2D vector shapes
    - voxel: the voxel structure is given with the voxel indices

The mesher is implemented with PyVista, Pillow, Shapely, and Rasterio.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import copy
import scilogger
from pypeec.lib_mesher import mesher_voxel
from pypeec.lib_mesher import mesher_shape
from pypeec.lib_mesher import mesher_png
from pypeec.lib_mesher import mesher_stl
from pypeec.lib_mesher import voxel_point
from pypeec.lib_mesher import voxel_conflict
from pypeec.lib_mesher import voxel_resampling
from pypeec.lib_mesher import voxel_integrity
from pypeec.lib_mesher import voxel_summary
from pypeec.lib_check import check_data_format

# get a logger
LOGGER = scilogger.get_logger(__name__, "pypeec")


def _run_mesher(data_geometry):
    """
    Run the mesher
    """

    # extract the input data
    mesh_type = data_geometry["mesh_type"]
    data_voxelize = data_geometry["data_voxelize"]

    # voxelize the geometry
    if mesh_type == "voxel":
        (reference, data_internal) = _run_voxel(data_voxelize)
    elif mesh_type == "shape":
        (reference, data_internal) = _run_shape(data_voxelize)
    elif mesh_type == "png":
        (reference, data_internal) = _run_png(data_voxelize)
    elif mesh_type == "stl":
        (reference, data_internal) = _run_stl(data_voxelize)
    else:
        raise ValueError("invalid mesh type")

    return reference, data_internal


def _run_voxel(data_voxelize):
    """
    Generate a 3D voxel structure from indices.
    """

    # extract the data
    param = data_voxelize["param"]
    domain_index = data_voxelize["domain_index"]

    # process the indices arrays
    with LOGGER.BlockTimer("mesher_voxel"):
        (n, d, c, domain_def, reference) = mesher_voxel.get_mesh(param, domain_index)

    # assemble the data
    data_internal = {
        "n": n,
        "d": d,
        "c": c,
        "domain_def": domain_def,
    }

    return reference, data_internal


def _run_shape(data_voxelize):
    """
    Generate a 3D voxel structure from 2D vector shapes.
    """

    # extract the data
    param = data_voxelize["param"]
    layer_stack = data_voxelize["layer_stack"]
    geometry_shape = data_voxelize["geometry_shape"]

    # process the shapes
    with LOGGER.BlockTimer("mesher_shape"):
        (n, d, c, domain_def, reference) = mesher_shape.get_mesh(param, layer_stack, geometry_shape)

    # assemble the data
    data_internal = {
        "n": n,
        "d": d,
        "c": c,
        "domain_def": domain_def,
    }

    return reference, data_internal


def _run_png(data_voxelize):
    """
    Generate a 3D voxel structure from PNG images.
    """

    # extract the data
    param = data_voxelize["param"]
    domain_color = data_voxelize["domain_color"]
    layer_stack = data_voxelize["layer_stack"]

    # voxelize the PNG files
    with LOGGER.BlockTimer("mesher_png"):
        (n, d, c, domain_def, reference) = mesher_png.get_mesh(param, domain_color, layer_stack)

    # assemble the data
    data_internal = {
        "n": n,
        "d": d,
        "c": c,
        "domain_def": domain_def,
    }

    return reference, data_internal


def _run_stl(data_voxelize):
    """
    Generate a 3D voxel structure from 3D STL files.
    """

    # extract the data
    param = data_voxelize["param"]
    domain_stl = data_voxelize["domain_stl"]

    # voxelize the STL files
    with LOGGER.BlockTimer("mesher_stl"):
        (n, d, c, domain_def, reference) = mesher_stl.get_mesh(param, domain_stl)

    # assemble the data
    data_internal = {
        "n": n,
        "d": d,
        "c": c,
        "domain_def": domain_def,
    }

    return reference, data_internal


def _run_resample_graph(reference, data_internal, data_geometry):
    """
    Resampling of a 3D voxel structure (increases the number of voxels).
    """

    # extract the data
    data_point = data_geometry["data_point"]
    data_resampling = data_geometry["data_resampling"]
    data_conflict = data_geometry["data_conflict"]
    data_integrity = data_geometry["data_integrity"]

    # extract the data
    n = data_internal["n"]
    d = data_internal["d"]
    c = data_internal["c"]
    domain_def = data_internal["domain_def"]

    with LOGGER.BlockTimer("voxel_point"):
        pts_cloud = voxel_point.get_point(n, d, c, domain_def, data_point)

    with LOGGER.BlockTimer("voxel_resampling"):
        (n, d, c, s, domain_def) = voxel_resampling.get_resampling(n, d, c, domain_def, data_resampling)

    with LOGGER.BlockTimer("voxel_conflict"):
        domain_def = voxel_conflict.get_conflict(domain_def, data_conflict)

    with LOGGER.BlockTimer("voxel_integrity"):
        graph_def = voxel_integrity.get_integrity(n, domain_def, data_integrity)

    with LOGGER.BlockTimer("voxel_summary"):
        voxel_status = voxel_summary.get_summary(n, d, s, c, pts_cloud, domain_def, graph_def)

    # assemble the data
    data_geom = {
        "n": n,
        "d": d,
        "s": s,
        "c": c,
        "voxel_status": voxel_status,
        "pts_cloud": pts_cloud,
        "domain_def": domain_def,
        "graph_def": graph_def,
        "reference": reference,
    }

    return data_geom


def _get_data(data_geom, timestamp):
    """
    Assemble the returned data.
    """

    # end message
    (seconds, duration, date) = scilogger.get_duration(timestamp)

    # get status
    status = True

    # extract the solution
    data_voxel = {
        "date": date,
        "duration": duration,
        "seconds": seconds,
        "status": status,
        "data_geom": data_geom,
    }

    return data_voxel


def run(data_geometry):
    """
    Main script for meshing the geometry and generating a 3D voxel structure.
    Handle invalid data with exceptions.
    """

    # get timestamp
    timestamp = scilogger.get_timestamp()

    # make copies of input data
    data_geometry = copy.deepcopy(data_geometry)

    # check the input data
    LOGGER.info("check the input data")
    check_data_format.check_data_geometry(data_geometry)

    # run the mesher
    (reference, data_internal) = _run_mesher(data_geometry)

    # resample and assemble
    data_geom = _run_resample_graph(reference, data_internal, data_geometry)

    # create output data
    data_voxel = _get_data(data_geom, timestamp)

    return data_voxel
