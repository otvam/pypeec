"""
Module for transforming a series of PNG images into a 3D voxel structure.
The 2D geometry are stacked in order to create a voxel structure.

The following axis definition is used:
    - x: x-axis of the images (standard cartesian coordinate, not image coordinate)
    - y: y-axis of the images (standard cartesian coordinate, not image coordinate)
    - z: stacking dimension of the 2D geometries

The image handling is done with Pillow.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import numpy as np
import PIL.Image as pmg
from pypeec import log
from pypeec import config
from pypeec.error import RunError

# get a logger
LOGGER = log.get_logger("STL")

# get config
NP_TYPES = config.NP_TYPES

# get problem size limits
VOXEL_TOTAL = config.PROBLEM_MAX_SIZE.VOXEL_TOTAL
VOXEL_USED = config.PROBLEM_MAX_SIZE.VOXEL_USED


def _get_load_image(filename_list):
    """
    Load several images into a list of tensors.
    Flip the axis in order to get standard cartesian coordinate (non-standard image coordinate).
    """

    # list for the images
    img_list = []

    # load the files
    for filename in filename_list:
        # load the image
        try:
            img = pmg.open(filename, formats=["png"])
        except OSError as ex:
            raise RunError("invalid png: invalid file content: %s" % filename) from ex

        # cast to array
        img = img.convert("RGBA")
        img = np.array(img, dtype=np.uint8)

        # transform from image coordinate to cartesian coordinate
        img = np.swapaxes(img, 0, 1)
        img = np.flip(img, axis=1)

        # store the loaded image
        img_list.append(img)

    return img_list


def _get_idx_image(size, img, color):
    """
    Get the 2D indices of an image that correspond to a specified color.
    """

    # get the image size
    (nx, ny) = size

    # check image
    if not (img.shape == (nx, ny, 4)):
        raise RunError("invalid image:  size is not compatible with the voxel structure")

    # get the color vector
    color_tmp = np.array(color, dtype=np.uint8)
    color_tmp = np.expand_dims(color_tmp, axis=(0, 1))
    if not (color_tmp.shape == (1, 1, 4)):
        raise RunError("invalid color: colors should be a specified with for values")

    # find the color in the image
    idx_img = np.all(img == color_tmp, axis=2)

    # find the 2D indices
    idx_img = idx_img.flatten(order="F")
    idx_img = np.flatnonzero(idx_img).astype(NP_TYPES.INT)

    return idx_img


def _get_idx_voxel(size, nz, n_layer, idx_img):
    """
    Find the 3D voxel indices from the 2D image indices.
    The number of layers to be added is arbitrary.
    """

    # get the image size
    (nx, ny) = size

    # init voxel indices
    idx_voxel = np.array([], dtype=NP_TYPES.INT)

    # convert image indices into voxel indices
    for iz in range(n_layer):
        # convert indices
        idx_tmp = (nz+iz)*nx*ny+idx_img

        # add the indices to the array
        idx_voxel = np.append(idx_voxel, idx_tmp)

    return idx_voxel


def _get_domain(size, nz, n_layer, color_list, img_list):
    """
    Find the voxels indices for a list a colors and a list of images.
    Convert the 2D image indices into 3D voxel indices.
    """

    # init the index array
    idx_img = np.array([], dtype=NP_TYPES.INT)

    # get image indices (2D indices)
    for color in color_list:
        for img in img_list:
            idx_img_tmp = _get_idx_image(size, img, color)
            idx_img = np.append(idx_img, idx_img_tmp)

    # remove duplicate (between the images in the list)
    idx_img = np.unique(idx_img)

    # get voxel indices (3D indices)
    idx_voxel = _get_idx_voxel(size, nz, n_layer, idx_img)

    return idx_voxel


def _get_layer(size, nz, domain_color, domain_def, n_layer, filename_list):
    """
    Find the voxel indices for a single layer.
    A single layer can be composed of several images.
    A single layer can contain several domains.
    """

    # extract the image data as a tensor
    img_list = _get_load_image(filename_list)

    # count the number of voxel for the layer
    n_voxel = 0

    # add the indices for all the domains
    for tag, color_list in domain_color.items():
        # get the indices of the voxels
        idx_voxel = _get_domain(size, nz, n_layer, color_list, img_list)

        # count the number of voxels
        n_voxel += len(idx_voxel)

        # append the indices into the corresponding domain
        domain_def[tag] = np.append(domain_def[tag], idx_voxel)

    # display the layer size
    LOGGER.debug("size = %d / n_voxels = %d" % (n_layer, n_voxel))

    # update the layer stack
    nz += n_layer

    return nz, domain_def


def get_mesh(param, domain_color, layer_stack):
    """
    Transform a series of PNG images into a 3D voxel structure.
    The 3D voxel structure is constructed from:
        - a dict mapping the pixel colors to domains
        - a list containing the layer stack of images
    """

    # extract the data
    d = param["d"]
    c = param["c"]
    size = param["size"]

    # no reference geometry, direct voxelization
    reference = None

    # get the image size
    (nx, ny) = size

    # init the layer stack
    nz = 0

    # init domain definition dict
    domain_def = {}
    for tag in domain_color:
        domain_def[tag] = np.array([], NP_TYPES.INT)

    # add layers
    for layer_stack_tmp in layer_stack:
        # extract the data
        n_layer = layer_stack_tmp["n_layer"]
        filename_list = layer_stack_tmp["filename_list"]

        # add the layer
        (nz, domain_def) = _get_layer(size, nz, domain_color, domain_def, n_layer, filename_list)

    # assemble
    n = (nx, ny, nz)

    # check total size
    nv = np.prod(n)
    if (VOXEL_TOTAL is not None) and (nv > VOXEL_TOTAL):
        raise RunError("invalid size of the voxel structure: %d" % nv)

    # check used size
    nv = sum(len(idx) for idx in domain_def.values())
    if (VOXEL_USED is not None) and (nv > VOXEL_USED):
        raise RunError("invalid number of used voxels: %d" % nv)

    return n, d, c, domain_def, reference
