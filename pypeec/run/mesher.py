"""
Main script for creating a 3D voxel structure.
Check the input data and mesh the structure.
The different parts of the code are timed.

Three different kind of geometry can be meshed:
    - The voxel structure is generated from 3D STL files.
    - The voxel structure is generated from stacked PNG images.
    - The voxel structure is generated from stacked 2D vector shapes.
    - The voxel structure is directly given with the voxel indices.

The mesher is implemented with PyVista, Pillow, Shapely, and Rasterio.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import copy
import scilogger
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
    Create and voxelize the geometry.
    """

    # extract the input data
    mesh_type = data_geometry["mesh_type"]
    data_voxelize = data_geometry["data_voxelize"]

    # voxelize the geometry
    if mesh_type == "voxel":
        (n, d, c, domain_def, geom_def) = _run_voxel(data_voxelize)
    elif mesh_type == "shape":
        (n, d, c, domain_def, geom_def) = _run_shape(data_voxelize)
    elif mesh_type == "png":
        (n, d, c, domain_def, geom_def) = _run_png(data_voxelize)
    elif mesh_type == "stl":
        (n, d, c, domain_def, geom_def) = _run_stl(data_voxelize)
    else:
        raise ValueError("invalid mesh type")

    return n, d, c, domain_def, geom_def


def _run_voxel(data_voxelize):
    """
    Generate a 3D voxel structure from given indices.
    """

    # load the mesher module
    from pypeec.lib_mesher import mesher_voxel

    # extract the data
    param = data_voxelize["param"]
    domain_index = data_voxelize["domain_index"]

    # process the indices arrays
    with LOGGER.BlockTimer("mesher_voxel"):
        (n, d, c, domain_def, geom_def) = mesher_voxel.get_mesh(
            param,
            domain_index,
        )

    return n, d, c, domain_def, geom_def


def _run_shape(data_voxelize):
    """
    Generate a 3D voxel structure from 2D vector shapes.
    """

    # load the mesher module
    from pypeec.lib_mesher import mesher_shape

    # extract the data
    param = data_voxelize["param"]
    layer_stack = data_voxelize["layer_stack"]
    geometry_shape = data_voxelize["geometry_shape"]

    # process the shapes
    with LOGGER.BlockTimer("mesher_shape"):
        (n, d, c, domain_def, geom_def) = mesher_shape.get_mesh(
            param,
            layer_stack,
            geometry_shape,
        )

    return n, d, c, domain_def, geom_def


def _run_png(data_voxelize):
    """
    Generate a 3D voxel structure from PNG images.
    """

    # load the mesher module
    from pypeec.lib_mesher import mesher_png

    # extract the data
    param = data_voxelize["param"]
    domain_color = data_voxelize["domain_color"]
    layer_stack = data_voxelize["layer_stack"]

    # voxelize the PNG files
    with LOGGER.BlockTimer("mesher_png"):
        (n, d, c, domain_def, geom_def) = mesher_png.get_mesh(
            param,
            domain_color,
            layer_stack,
        )

    return n, d, c, domain_def, geom_def


def _run_stl(data_voxelize):
    """
    Generate a 3D voxel structure from 3D STL files.
    """

    # load the mesher module
    from pypeec.lib_mesher import mesher_stl

    # extract the data
    param = data_voxelize["param"]
    domain_stl = data_voxelize["domain_stl"]

    # voxelize the STL files
    with LOGGER.BlockTimer("mesher_stl"):
        (n, d, c, domain_def, geom_def) = mesher_stl.get_mesh(
            param,
            domain_stl,
        )

    return n, d, c, domain_def, geom_def


def _run_finalize(n, d, c, domain_def, geom_def, data_geometry):
    """
    Finalize the generated geometry:
        - Generate the point cloud.
        - Resampling the voxel structure.
        - Resolve conflicts for the voxel structure.
        - Check the connections inside the voxel structure.
        - Summarize the properties of the mesh.
    """

    # extract the data
    data_point = data_geometry["data_point"]
    data_resampling = data_geometry["data_resampling"]
    data_conflict = data_geometry["data_conflict"]
    data_integrity = data_geometry["data_integrity"]

    with LOGGER.BlockTimer("voxel_point"):
        pts_cloud = voxel_point.get_point(
            n,
            d,
            c,
            domain_def,
            data_point,
        )

    with LOGGER.BlockTimer("voxel_resampling"):
        (n, d, c, s, domain_def) = voxel_resampling.get_resampling(
            n,
            d,
            c,
            domain_def,
            data_resampling,
        )

    with LOGGER.BlockTimer("voxel_conflict"):
        domain_def = voxel_conflict.get_conflict(
            domain_def,
            data_conflict,
        )

    with LOGGER.BlockTimer("voxel_integrity"):
        (component_def, connect_def) = voxel_integrity.get_integrity(
            n,
            domain_def,
            data_integrity,
        )

    with LOGGER.BlockTimer("voxel_summary"):
        voxel_status = voxel_summary.get_summary(
            n,
            d,
            s,
            c,
            pts_cloud,
            domain_def,
            component_def,
        )

    # assemble the data
    data = {
        "d": d,  # tuple with the size of a single voxel
        "n": n,  # tuple with the number of voxels composing structure
        "s": s,  # tuple with the total size of the structure
        "c": c,  # tuple with the center of the voxel structure
        "voxel_status": voxel_status,  # dict with a summary of the voxel structure
        "pts_cloud": pts_cloud,  # array with coordinates of the point cloud
        "domain_def": domain_def,  # dict with the indices of the different domains
        "component_def": component_def,  # list with the indices of the connected components
        "connect_def": connect_def,  # dict describing the connected/adjacent domains
        "geom_def": geom_def,  # list of meshes representing the original geometry
    }

    return data


def run(data_geometry):
    """
    Main script for meshing the geometry and generating a 3D voxel structure.
    Handle invalid data with exceptions.
    """

    # make copies of input data
    data_geometry = copy.deepcopy(data_geometry)

    # check the input data
    LOGGER.info("check the input data")
    check_data_format.check_data_geometry(data_geometry)

    # run the mesher
    (n, d, c, domain_def, geom_def) = _run_mesher(data_geometry)

    # finalize the mesh
    data_voxel = _run_finalize(n, d, c, domain_def, geom_def, data_geometry)

    return data_voxel
