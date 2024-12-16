"""
Different functions for checking the integrity of the voxel structure.
First, a sparse undirected graph is constructed from the voxel structure.
The graph is used to check for connected and adjacent domains.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import numpy as np
import scipy.sparse as sps
import scipy.sparse.csgraph as csg


def _get_all_indices(domain_def):
    """
    Get the indices of the non-empty voxels for all the domains.
    """

    # init
    idx = np.empty(0, dtype=np.int64)

    # get the indices and colors
    for tag in domain_def:
        idx = np.append(idx, domain_def[tag])

    return idx


def _get_group_indices(domain_def, domain_group):
    """
    Get the indices of the non-empty voxels for the given domains.
    """

    group_def = []
    for domain_group_tmp in domain_group:
        # init
        idx_tmp = np.empty(0, dtype=np.int64)

        # get the indices and colors
        for tag in domain_group_tmp:
            # check domain
            if tag not in domain_def:
                raise RuntimeError("invalid domain: name not found: %s" % tag)

            # add indices
            idx_tmp = np.append(idx_tmp, domain_def[tag])

        if len(idx_tmp) > 0:
            group_def.append(idx_tmp)

    return group_def


def _get_connection_matrix(n):
    """
    Get a sparse matrix describing the connection between the voxels.
    This matrix is extracted for the complete voxel structure.
    """

    # extract the voxel data
    (nx, ny, nz) = n

    # get total size
    nv = np.prod(n)

    # voxel index array
    x = np.arange(nx, dtype=np.int64)
    y = np.arange(ny, dtype=np.int64)
    z = np.arange(nz, dtype=np.int64)
    (idx_x, idx_y, idx_z) = np.meshgrid(x, y, z, indexing="ij")

    # voxel index number
    idx = idx_x + idx_y * nx + idx_z * nx * ny

    # create the sparse matrix
    voxel_matrix = sps.csc_matrix((nv, nv), dtype=np.int64)

    # self connections
    idx_col = np.arange(nv)
    idx_row = np.arange(nv)
    data = np.ones(nv, dtype=np.int64)
    voxel_matrix += sps.csc_matrix((data, (idx_row, idx_col)), shape=(nv, nv), dtype=np.int64)

    # connections along x direction
    idx_col = idx[:-1, :, :].flatten()
    idx_row = idx[+1:, :, :].flatten()
    data = np.ones((nx - 1) * ny * nz, dtype=np.int64)
    voxel_matrix += sps.csc_matrix((data, (idx_row, idx_col)), shape=(nv, nv), dtype=np.int64)
    voxel_matrix += sps.csc_matrix((data, (idx_col, idx_row)), shape=(nv, nv), dtype=np.int64)

    # connections along y direction
    idx_col = idx[:, :-1, :].flatten()
    idx_row = idx[:, +1:, :].flatten()
    data = np.ones(nx * (ny - 1) * nz, dtype=np.int64)
    voxel_matrix += sps.csc_matrix((data, (idx_row, idx_col)), shape=(nv, nv), dtype=np.int64)
    voxel_matrix += sps.csc_matrix((data, (idx_col, idx_row)), shape=(nv, nv), dtype=np.int64)

    # connections along z direction
    idx_col = idx[:, :, :-1].flatten()
    idx_row = idx[:, :, +1:].flatten()
    data = np.ones(nx * ny * (nz - 1), dtype=np.int64)
    voxel_matrix += sps.csc_matrix((data, (idx_row, idx_col)), shape=(nv, nv), dtype=np.int64)
    voxel_matrix += sps.csc_matrix((data, (idx_col, idx_row)), shape=(nv, nv), dtype=np.int64)

    return voxel_matrix


def _get_connected_components(graph_matrix, idx):
    """
    Get the connected components in the graph.
    """

    # find the connected components in the graph
    (n_comp, labels) = csg.connected_components(
        csgraph=graph_matrix,
        directed=False,
        return_labels=True,
    )

    # get the indices of the connected components
    graph_def = []
    for i in range(n_comp):
        idx_local = labels == i
        idx_graph = idx[idx_local]
        graph_def.append(idx_graph)

    return graph_def


def _check_domain_connected(domain_def, graph_def, domain_connected, tag):
    """
    Check that the given connections between the domain exists.
    """

    # extract the data
    domain_group = domain_connected["domain_group"]
    connected = domain_connected["connected"]

    # merge group and remove empty domains
    group_def = _get_group_indices(domain_def, domain_group)

    # init the connection matrix
    matrix = np.full((len(graph_def), len(group_def)), True, dtype=bool)

    # fill the connection matrix
    for i, idx_graph in enumerate(graph_def):
        for j, idx_group in enumerate(group_def):
            idx_shared = np.intersect1d(idx_graph, idx_group)
            matrix[i, j] = len(idx_shared) > 0

    # count connection
    vector = np.count_nonzero(matrix, axis=1)

    # check validity
    if connected:
        idx_ok = vector == len(group_def)
        if not np.any(idx_ok):
            raise RuntimeError("domain connection is missing: %s" % tag)
    else:
        idx_ok = np.logical_or(vector == 0, vector == 1)
        if not np.all(idx_ok):
            raise RuntimeError("domain connection is illegal: %s" % tag)


def _check_domain_adjacent(domain_def, voxel_matrix, domain_connected, tag):
    """
    Check that the given connections between the domain exists.
    """

    # extract the data
    domain_group = domain_connected["domain_group"]
    connected = domain_connected["connected"]

    # merge group and remove empty domains
    group_def = _get_group_indices(domain_def, domain_group)

    # init the connection matrix
    matrix = np.full((len(group_def), len(group_def)), True, dtype=bool)

    # fill the connection matrix
    for i, idx_group_i in enumerate(group_def):
        for j, idx_group_j in enumerate(group_def):
            idx_shared = voxel_matrix[idx_group_i, :][:, idx_group_j]
            matrix[i, j] = idx_shared.count_nonzero() > 0

    # count connection
    vector = np.count_nonzero(matrix, axis=1)

    # check validity
    if connected:
        idx_ok = vector == len(group_def)
        if not np.any(idx_ok):
            raise RuntimeError("domain connection is missing: %s" % tag)
    else:
        idx_ok = np.logical_or(vector == 0, vector == 1)
        if not np.all(idx_ok):
            raise RuntimeError("domain connection is illegal: %s" % tag)


def get_integrity(n, domain_def, data_integrity):
    """
    Find the connected components of a voxel structure.
    """

    # extract the data
    domain_connected = data_integrity["domain_connected"]
    domain_adjacent = data_integrity["domain_adjacent"]

    # get the indices of the non-empty voxels
    idx = _get_all_indices(domain_def)

    # get the connection matrix between the voxels
    voxel_matrix = _get_connection_matrix(n)

    # get the graph matrix
    graph_matrix = voxel_matrix
    graph_matrix = graph_matrix[idx, :]
    graph_matrix = graph_matrix[:, idx]

    # find the connected components in the graph
    graph_def = _get_connected_components(graph_matrix, idx)

    # check the connections between the adjacent domains
    for tag, domain_tmp in domain_adjacent.items():
        _check_domain_adjacent(domain_def, voxel_matrix, domain_tmp, tag)

    # check the connection between the connected components
    for tag, domain_tmp in domain_connected.items():
        _check_domain_connected(domain_def, graph_def, domain_tmp, tag)

    return graph_def
