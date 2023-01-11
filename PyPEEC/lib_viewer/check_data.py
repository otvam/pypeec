"""
Module for checking the viewer input data.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np


class CheckError(Exception):
    """
    Exception used for signaling invalid input data.
    """

    pass


def _check_domain_def(n, domain_def):
    """
    Check that the domain definition is valid.
    """

    # extract the voxel data
    (nx, ny, nz) = n
    n = nx * ny * nz

    # init the domain indices
    idx_domain = np.array([], dtype=np.int64)

    # check type
    if not isinstance(domain_def, dict):
        raise CheckError("domain_def: domain definition should be a dict")

    # check the different domains
    for tag, idx in domain_def.items():
        # check tag
        if not isinstance(tag, str):
            raise CheckError("tag: conductor name should be a string")

        # cast indices
        idx = np.array(idx)
        if not (len(idx.shape) == 1):
            raise CheckError("idx: indices should be a vector")
        if not np.issubdtype(idx.dtype, np.integer):
            raise CheckError("idx: indices should be composed of integers")

        # check for indices range
        if not (np.all(idx >= 0) and np.all(idx < n)):
            raise CheckError("idx: conductor indices should belong to the voxel structure")

        # append
        idx_domain = np.append(idx_domain, idx)

    # check for duplicates
    if not (len(np.unique(idx_domain)) == len(idx_domain)):
        raise CheckError("domain indices should be unique")


def _check_plot_options(plot_options):
    """
    Check the validity of the plot options.
    The plot options are controlling the wireframes and the origin marker.
    """

    # check type
    if not isinstance(plot_options, dict):
        raise CheckError("plot_options: plot options should be a dict")

    # check grid options (plot of the complete grid as wireframes)
    if not isinstance(plot_options["grid_plot"], bool):
        raise CheckError("grid_plot: the grid plot option should be a boolean")
    if not isinstance(plot_options["grid_thickness"], float):
        raise CheckError("grid_thickness: the grid thickness option should be a float")
    if not isinstance(plot_options["grid_color"], str):
        raise CheckError("grid_color: the grid color option should be a string")
    if not isinstance(plot_options["grid_opacity"], float):
        raise CheckError("grid_opacity: the grid opacity option should be a float")

    # check geom options (plot of the non-empty voxels as wireframe)
    if not isinstance(plot_options["geom_plot"], bool):
        raise CheckError("geom_plot: the geom plot option should be a boolean")
    if not isinstance(plot_options["geom_thickness"], float):
        raise CheckError("geom_thickness: the geom thickness option should be a float")
    if not isinstance(plot_options["geom_color"], str):
        raise CheckError("geom_color: the geom color option should be a string")
    if not isinstance(plot_options["geom_opacity"], float):
        raise CheckError("geom_opacity: the geom opacity option should be a float")

    # check origin options (add a marker at the origin)
    if not isinstance(plot_options["origin_plot"], bool):
        raise CheckError("origin_plot: the origin plot option should be a boolean")
    if not isinstance(plot_options["origin_size"], float):
        raise CheckError("origin_size: the origin size option should be a float")
    if not isinstance(plot_options["origin_color"], str):
        raise CheckError("origin_color: the origin color option should be a string")


def check_data_viewer(data_viewer):
    """
    Check the validity of the dict describing a plot.
    """

    # check type
    if not isinstance(data_viewer, dict):
        raise CheckError("data_viewer: the plot description should be a dict")

    # extract field
    window_title = data_viewer["window_title"]
    plot_title = data_viewer["plot_title"]
    window_size = data_viewer["window_size"]
    plot_options = data_viewer["plot_options"]

    # check type
    if not isinstance(window_title, str):
        raise CheckError("window_title: window title should be a string")
    if not isinstance(plot_title, str):
        raise CheckError("plot_title: plot title should be a string")
    if not isinstance(plot_options, dict):
        raise CheckError("plot_options: plot options should be a dict")

    # check size
    if not len(window_size)==2:
        raise CheckError("invalid window size (should be a tuple with two elements)")

    # check value
    if not all(isinstance(x, int) for x in window_size):
        raise CheckError("window_size: window size should be composed of integers")
    if not all((x >= 1) for x in window_size):
        raise CheckError("window_size: window size should be greater than zero")

    # check data and plot options
    _check_plot_options(plot_options)


def check_data_voxel(data_voxel):
    """
    Check the voxel structure (number and size).
    Check the domain definition (mapping between domain names and indices).
    """

    # check type
    if not isinstance(data_voxel, dict):
        raise CheckError("data_voxel: voxel description should be a dict")

    # extract field
    n = data_voxel["n"]
    d = data_voxel["d"]
    domain_def = data_voxel["domain_def"]

    # check size
    if not (len(n) == 3):
        raise CheckError("n: invalid voxel number (should be a tuple with three elements)")
    if not (len(d) == 3):
        raise CheckError("d: invalid voxel size (should be a tuple with three elements)")

    # check type
    if not all(np.issubdtype(type(x), np.integer) for x in n):
        raise CheckError("n: number of voxels should be composed of integers")
    if not all(np.issubdtype(type(x), np.floating) for x in d):
        raise CheckError("d: dimension of the voxels should be composed of real floats")

    # check value
    if not all((x >= 1) for x in n):
        raise CheckError("n: number of voxels cannot be smaller than one")
    if not all((x > 0) for x in d):
        raise CheckError("d: dimension of the voxels should be positive")

    # check domain
    _check_domain_def(n, domain_def)
