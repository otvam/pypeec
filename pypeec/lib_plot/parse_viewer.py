"""
Add data to the PyVista objects for the viewer:
    - Assign an integer variable to the different domains composing the voxel structure.
    - Assign an integer variable to the connected components of the voxel structure.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import numpy as np


def _get_connected_component(idx, component_def):
    """
    Find the connected components for a specific domain.
    Assign a different scalar for each connected component.
    """

    # init the data with invalid data
    component = np.zeros(len(idx), dtype=np.int64)

    # find to corresponding connected components
    for counter, idx_component in enumerate(component_def):
        # find which indices are part of the connected component
        idx_ok = np.isin(idx, idx_component)

        # assign the component number to the corresponding indices
        component[idx_ok] = counter + 1

    # check that everything was assigned
    if not np.all(component):
        raise RuntimeError("some voxels are not part of the graph")

    return component


def _get_component_tag(domain_def, component_def):
    """
    Assign a different integer for each connected component.
    """

    # init data
    connected_tag = np.empty(0, dtype=np.int64)

    # get the connected component tags
    for idx_tmp in domain_def.values():
        connected_tmp = _get_connected_component(idx_tmp, component_def)
        connected_tag = np.append(connected_tag, connected_tmp)

    return connected_tag


def _get_domain_tag(domain_def):
    """
    Assign a different integer for each domain.
    """

    # init data
    domain_tag = np.empty(0, dtype=np.int64)

    # get the domain tags
    for counter, idx_tmp in enumerate(domain_def.values()):
        domain_tmp = np.full(len(idx_tmp), counter + 1, dtype=np.int64)
        domain_tag = np.append(domain_tag, domain_tmp)

    return domain_tag


def set_data(voxel, idx, domain_def, component_def):
    """
    Add the domain and connected component description to the unstructured grid.
    Integers are used to encode the different tags.
    """

    # get the data
    domain_tag = _get_domain_tag(domain_def)
    component_tag = _get_component_tag(domain_def, component_def)

    # sort data with the indices
    idx = np.argsort(idx)
    domain_tag = domain_tag[idx]
    component_tag = component_tag[idx]

    # assign the data to the geometry
    voxel["domain_tag"] = domain_tag
    voxel["component_tag"] = component_tag

    return voxel


def get_voxel(domain_def):
    """
    Get the indices of the non-empty voxels.
    """

    idx = np.empty(0, dtype=np.int64)
    for idx_tmp in domain_def.values():
        idx = np.append(idx, idx_tmp)

    return idx
