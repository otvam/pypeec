"""
Different functions for finding the connected components of a voxel structure.
First, a sparse undirected graph is constructed from the voxel structure.
Afterwards, the connected components of the graph are extracted.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import numpy as np
import scipy.sparse as sps
import scipy.sparse.csgraph as csg
from pypeec import config
from pypeec.error import RunError

# get config
NP_TYPES = config.NP_TYPES


def _get_domain_indices(domain_def):
    """
    Get the indices of the non-empty voxels.
    """

    # init
    idx = np.empty(0, dtype=NP_TYPES.INT)

    # get the indices and colors
    for idx_tmp in domain_def.values():
        idx = np.append(idx, idx_tmp)

    return idx


def _get_connection_matrix(n):
    """
    Get a sparse matrix describing the connection between the voxels.
    This matrix is extracted for the complete voxel structure.
    """

    # extract the voxel data
    (nx, ny, nz) = n
    nv = nx*ny*nz

    # voxel index array
    x = np.arange(nx, dtype=NP_TYPES.INT)
    y = np.arange(ny, dtype=NP_TYPES.INT)
    z = np.arange(nz, dtype=NP_TYPES.INT)
    (idx_x, idx_y, idx_z) = np.meshgrid(x, y, z, indexing="ij")

    # voxel index number
    idx = idx_x+idx_y*nx+idx_z*nx*ny

    # create the sparse matrix
    A_connection = sps.csc_matrix((nv, nv), dtype=NP_TYPES.INT)

    # connections along x direction
    idx_col = idx[0:-1, :, :].flatten()
    idx_row = idx[1:, :, :].flatten()
    data = np.ones((nx-1)*ny*nz, dtype=NP_TYPES.INT)
    A_connection += sps.csc_matrix((data, (idx_row, idx_col)), shape=(nv, nv), dtype=NP_TYPES.INT)

    # connections along y direction
    idx_col = idx[:, 0:-1, :].flatten()
    idx_row = idx[:, 1:, :].flatten()
    data = np.ones(nx*(ny-1)*nz, dtype=NP_TYPES.INT)
    A_connection += sps.csc_matrix((data, (idx_row, idx_col)), shape=(nv, nv), dtype=NP_TYPES.INT)

    # connections along z direction
    idx_col = idx[:, :, 0:-1].flatten()
    idx_row = idx[:, :, 1:].flatten()
    data = np.ones(nx*ny*(nz-1), dtype=NP_TYPES.INT)
    A_connection += sps.csc_matrix((data, (idx_row, idx_col)), shape=(nv, nv), dtype=NP_TYPES.INT)

    return A_connection


def _check_domain_connection(domain_def, connection_def, tag_connection, data_connection):
    """
    Check that the given connections between the domain exists.
    """

    # extract the data
    domain_list = data_connection["domain_list"]
    connected = data_connection["connected"]

    # remove empty domains
    domain_filtered = []
    for tag in domain_list:
        idx_domain = domain_def[tag]
        if len(idx_domain) > 0:
            domain_filtered.append(tag)

    # init the connection matrix
    matrix = np.full((len(connection_def), len(domain_filtered)), True, dtype=bool)

    # fill the connection matrix
    for i, idx_graph in enumerate(connection_def):
        for j, tag in enumerate(domain_filtered):
            idx_domain = domain_def[tag]
            idx_shared = np.intersect1d(idx_graph, idx_domain)
            matrix[i, j] = len(idx_shared) > 0

    # check connection
    vector = np.count_nonzero(matrix, axis=1)

    # check connection
    if connected:
        idx_ok = vector == len(domain_filtered)
        if not np.any(idx_ok):
            raise RunError("domain connection: domain connection is missing: %s" % tag_connection)
    else:
        idx_ok = np.logical_or(vector == 0, vector == 1)
        if not np.all(idx_ok):
            raise RunError("domain connection: domain connection is illegal: %s" % tag_connection)


def get_connection(n, domain_def, domain_connection):
    """
    Find the connected components of a voxel structure.
    """

    # get the indices of the non-empty voxels
    idx = _get_domain_indices(domain_def)

    # get the connection matrix between the voxels
    A_connection = _get_connection_matrix(n)

    # get the graph matrix
    A_graph = A_connection
    A_graph = A_graph[idx, :]
    A_graph = A_graph[:, idx]

    # find the connected components in the graph
    (n_comp, labels) = csg.connected_components(
        csgraph=A_graph,
        directed=False,
        return_labels=True,
    )

    # get the indices of the connected components
    connection_def = []
    for i in range(n_comp):
        idx_local = labels == i
        idx_graph = idx[idx_local]
        connection_def.append(idx_graph)

    # check the connections between the domains
    for tag, dat_tmp in domain_connection.items():
        _check_domain_connection(domain_def, connection_def, tag, dat_tmp)

    return connection_def
