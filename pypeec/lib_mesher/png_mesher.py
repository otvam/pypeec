"""
Module for transforming a series of 2D PNG images into a 3D voxel structure.

The following axis definition is used:
    - x: x-axis of the images (standard cartesian coordinate, not image coordinate)
    - y: y-axis of the images (standard cartesian coordinate, not image coordinate)
    - z: defined with the layer stack defining the 2D images
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import numpy as np
import PIL.Image as pmg
from pypeec.lib_utils.error import RunError


def _get_idx_image(nx, ny, img, color):
    """
    Get the 2D indices of an image that correspond to a specified color.
    """

    # check image
    if not (img.shape == (nx, ny, 4)):
        raise RunError("invalid image:  size is not compatible with the voxel structure")

    # get the color vector
    color_tmp = np.array(color, dtype=np.int_)
    color_tmp = np.expand_dims(color_tmp, axis=(0, 1))
    if not (color_tmp.shape == (1, 1, 4)):
        raise RunError("invalid color: colors should be a specified with for values")

    # find the color in the image
    idx_img = np.all(img == color_tmp, axis=2)

    # find the 2D indices
    idx_img = idx_img.flatten(order="F")
    idx_img = np.flatnonzero(idx_img)

    return idx_img


def _get_idx_voxel(nx, ny, nz, n_layer, idx_img):
    """
    Find the 3D voxel indices from the 2D image indices.
    The number of layers to be added is arbitrary.
    """

    # init idx
    idx_voxel = np.array([], dtype=np.int_)

    # convert image indices into voxel indices
    for n_tmp in range(n_layer):
        # convert indices
        idx_tmp = (nz+n_tmp)*nx*ny+idx_img

        # add the indices to the array
        idx_voxel = np.append(idx_voxel, idx_tmp)

    return idx_voxel


def _get_image(filename):
    """
    Load an image into a tensor.
    Flip the axis in order to get standard cartesian coordinate (non-standard image coordinate).
    """

    # load the image
    try:
        img = pmg.open(filename, formats=["png"])
    except OSError:
        raise RunError("invalid png: invalid file content: %s" % filename)

    # cast to array
    img = np.array(img)

    # transform from image coordinate to cartesian coordinate
    img = np.swapaxes(img, 0, 1)
    img = np.flip(img, axis=1)

    return img


def _get_layer(nx, ny, nz, domain_color, domain_def, n_layer, filename):
    """
    Add an image to the 3D voxel structure.
    Update the domain indices and the number of layers.
    """

    # extract the image data as a tensor
    img = _get_image(filename)

    # add the indices for all the domains
    for tag, color in domain_color.items():
        # get image indices (2D indices)
        idx_img = _get_idx_image(nx, ny, img, color)

        # get voxel indices (3D indices)
        idx_voxel = _get_idx_voxel(nx, ny, nz, n_layer, idx_img)

        # append the indices into the corresponding domain
        domain_def[tag] = np.append(domain_def[tag], idx_voxel)

    # update the layer stack
    nz += n_layer

    return nz, domain_def


def get_mesh(nx, ny, domain_color, layer_stack):
    """
    Transform a series of 2D PNG images into a 3D voxel structure.
    The 3D voxel structure is constructed from:
        - a dict mapping the pixel colors to domains
        - a list containing the layer stack of images
    """

    # init the layer stack
    nz = 0

    # init domain definition dict
    domain_def = {}
    for tag, color in domain_color.items():
        domain_def[tag] = np.array([], np.int_)

    # add layers
    for layer_stack_tmp in layer_stack:
        # get the data
        n_layer = layer_stack_tmp["n_layer"]
        filename = layer_stack_tmp["filename"]

        # add the layer
        (nz, domain_def) = _get_layer(nx, ny, nz, domain_color, domain_def, n_layer, filename)

    # assemble
    n = (nx, ny, nz)

    return n, domain_def