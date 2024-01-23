"""
Add data to the PyVista objects for the viewer:
    - domain description
    - connected component
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import numpy as np
from pypeec.error import RunError


def _get_graph_component(idx, connection_def):
    """
    Find the connected components for a specific domain.
    Assign a different scalar for each connected component.
    """

    # init the data with invalid data
    if len(connection_def) == 0:
        tag = np.ones(len(idx), dtype=np.int_)
    else:
        tag = np.zeros(len(idx), dtype=np.int_)

    # find to corresponding connected components
    for i, idx_graph in enumerate(connection_def):
        # find which indices are part of the connected component
        idx_ok = np.in1d(idx, idx_graph)

        # assign the component number to the corresponding indices
        tag[idx_ok] = i+1

    # check that everything was assigned
    if not np.all(tag):
        raise RunError("invalid graph: some voxels are not part of the graph")

    return tag


def _get_geometry_tag(domain_def, connection_def):
    """
    Assign a different integer for each domain.
    Assign a different integer for each connected component.
    """

    # init
    domain = np.empty(0, dtype=np.int_)
    connection = np.empty(0, dtype=np.int_)

    # get the indices and colors
    counter = 1
    for tag, idx_tmp in domain_def.items():
        # assign the color (n different integer for each domain)
        domain_tmp = np.full(len(idx_tmp), counter, dtype=np.int_)

        # find the connected components corresponding to the indices
        connection_tmp = _get_graph_component(idx_tmp, connection_def)

        # append the indices and colors
        domain = np.append(domain, domain_tmp)
        connection = np.append(connection, connection_tmp)

        # update the domain counter
        counter += 1

    return domain, connection


def set_data(voxel, idx, domain_def, connection_def):
    """
    Add the domain and connected component description to the unstructured grid.
    Integers are used to encode the different tags.
    """

    # get the data
    (domain, connection) = _get_geometry_tag(domain_def, connection_def)

    # get sorted indices
    idx = np.argsort(idx)

    # sort data
    domain = domain[idx]
    connection = connection[idx]

    # assign the data to the geometry
    voxel["domain"] = domain
    voxel["connection"] = connection

    return voxel


def get_voxel(domain_def):
    """
    Get the indices of the non-empty voxels.
    """

    idx = np.empty(0, dtype=np.int_)
    for idx_tmp in domain_def.values():
        idx = np.append(idx, idx_tmp)

    return idx
