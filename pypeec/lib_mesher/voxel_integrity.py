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


def _get_component(graph_matrix, idx):
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
    component_def = []
    for i in range(n_comp):
        idx_local = labels == i
        idx_component = idx[idx_local]
        component_def.append(idx_component)

    return component_def


def _check_domain_rule(domain_group, connected, tag_list, mat, tag):
    """
    Check a rule between domain groups.
    """

    # init the connection matrix
    rule = np.full((len(domain_group), len(domain_group)), True, dtype=bool)

    # fill the connection matrix
    for i, tag_group_i in enumerate(domain_group):
        for j, tag_group_j in enumerate(domain_group):
            idx_i = np.flatnonzero(np.isin(tag_list, tag_group_i))
            idx_j = np.flatnonzero(np.isin(tag_list, tag_group_j))
            rule[i, j] = np.any(mat[idx_i, idx_j])

    # count connection
    rule = np.count_nonzero(rule, axis=1)

    # check validity
    if connected:
        idx_ok = rule == len(domain_group)
        if not np.any(idx_ok):
            raise RuntimeError("domain connection is missing: %s" % tag)
    else:
        idx_ok = np.logical_or(rule == 0, rule == 1)
        if not np.all(idx_ok):
            raise RuntimeError("domain connection is illegal: %s" % tag)


def _check_domain_connected(connect_def, domain_connected, tag):
    """
    Check that the given domains are in a connected component.
    """

    # extract the data
    domain_group = domain_connected["domain_group"]
    connected = domain_connected["connected"]

    # extract the data
    tag_list = connect_def["tag_list"]
    connected_mat = connect_def["connected_mat"]

    # check the rule
    _check_domain_rule(domain_group, connected, tag_list, connected_mat, tag)


def _check_domain_adjacent(connect_def, domain_connected, tag):
    """
    Check that the given domains are adjacent between each others.
    """

    # extract the data
    domain_group = domain_connected["domain_group"]
    connected = domain_connected["connected"]

    # extract the data
    tag_list = connect_def["tag_list"]
    adjacent_mat = connect_def["adjacent_mat"]

    # check the rule
    _check_domain_rule(domain_group, connected, tag_list, adjacent_mat, tag)


def _get_connect(domain_def, component_def, voxel_matrix):
    """
    Find the connection matrices between the domains (connected components and adjacent domains).
    """

    # get the domains
    tag_list = list(domain_def.keys())

    # init the connection data
    connected_mat = np.zeros((len(tag_list), len(tag_list)), dtype=bool)
    adjacent_mat = np.zeros((len(tag_list), len(tag_list)), dtype=bool)

    # build the matrices
    for i, idx_i in enumerate(domain_def.values()):
        for j, idx_j in enumerate(domain_def.values()):
            # find the connected domains
            for idx_component in component_def:
                connected_i = len(np.intersect1d(idx_component, idx_i)) > 0
                connected_j = len(np.intersect1d(idx_component, idx_j)) > 0
                connected_mat[i, j] = connected_mat[i, j] or (connected_i and connected_j)

            # find the adjacent domains
            idx_shared = voxel_matrix[idx_i, :][:, idx_j]
            adjacent_mat[i, j] = idx_shared.count_nonzero() > 0

    # assign the data
    connect_def = {"tag_list": tag_list, "connected_mat": connected_mat, "adjacent_mat": adjacent_mat}

    return connect_def


def get_integrity(n, domain_def, data_integrity):
    """
    Find the connected components of a voxel structure.
    """

    # extract the data
    check_integrity = data_integrity["check_integrity"]
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
    component_def = _get_component(graph_matrix, idx)

    # get the connection between the domains
    connect_def = _get_connect(domain_def, component_def, voxel_matrix)

    # check the voxel structure (if required)
    if check_integrity:
        # check the connections between the adjacent domains
        for tag, domain_tmp in domain_adjacent.items():
            _check_domain_adjacent(connect_def, domain_tmp, tag)

        # check the connection between the connected components
        for tag, domain_tmp in domain_connected.items():
            _check_domain_connected(connect_def, domain_tmp, tag)

    return component_def, connect_def
