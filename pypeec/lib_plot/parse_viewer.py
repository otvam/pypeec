"""
Add data to the PyVista objects for the viewer:
    - domain description
    - connected component
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import numpy as np


def _get_graph_component(idx, graph_def):
    """
    Find the connected components for a specific domain.
    Assign a different scalar for each connected component.
    """

    # init the data with invalid data
    graph = np.zeros(len(idx), dtype=np.int64)

    # find to corresponding connected components
    for i, idx_graph in enumerate(graph_def):
        # find which indices are part of the connected component
        idx_ok = np.isin(idx, idx_graph)

        # assign the component number to the corresponding indices
        graph[idx_ok] = i + 1

    # check that everything was assigned
    if not np.all(graph):
        raise RuntimeError("some voxels are not part of the graph")

    return graph


def _get_geometry_tag(domain_def, graph_def):
    """
    Assign a different integer for each domain.
    Assign a different integer for each connected component.
    """

    # init
    domain = np.empty(0, dtype=np.int64)
    graph = np.empty(0, dtype=np.int64)

    # get the indices and colors
    counter = 1
    for idx_tmp in domain_def.values():
        # assign the color (n different integer for each domain)
        domain_tmp = np.full(len(idx_tmp), counter, dtype=np.int64)

        # find the connected components corresponding to the indices
        graph_tmp = _get_graph_component(idx_tmp, graph_def)

        # append the indices and colors
        domain = np.append(domain, domain_tmp)
        graph = np.append(graph, graph_tmp)

        # update the domain counter
        counter += 1

    return domain, graph


def set_data(voxel, idx, domain_def, graph_def):
    """
    Add the domain and connected component description to the unstructured grid.
    Integers are used to encode the different tags.
    """

    # get the data
    (domain, graph) = _get_geometry_tag(domain_def, graph_def)

    # get sorted indices
    idx = np.argsort(idx)

    # sort data
    domain = domain[idx]
    graph = graph[idx]

    # assign the data to the geometry
    voxel["domain"] = domain
    voxel["graph"] = graph

    return voxel


def get_voxel(domain_def):
    """
    Get the indices of the non-empty voxels.
    """

    idx = np.empty(0, dtype=np.int64)
    for idx_tmp in domain_def.values():
        idx = np.append(idx, idx_tmp)

    return idx
