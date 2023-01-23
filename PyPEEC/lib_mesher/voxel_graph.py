"""
Different functions for finding the connected components of a voxel structure.
Find the indices of the different connected components of the graph.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np
import scipy.sparse as sps
import scipy.sparse.csgraph as csg


def _get_domain_indices(domain_def):
    """
    Get the indices of the non-empty voxels.
    """

    # init
    idx = np.empty(0, dtype=np.int64)

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
    n = nx*ny*nz

    # voxel index array
    x = np.arange(nx, dtype=np.int64)
    y = np.arange(ny, dtype=np.int64)
    z = np.arange(nz, dtype=np.int64)
    (idx_x, idx_y, idx_z) = np.meshgrid(x, y, z, indexing="ij")

    # voxel index number
    idx = idx_x+idx_y*nx+idx_z*nx*ny

    # create the sparse matrix
    A_connection = sps.csc_matrix((n, n), dtype=np.int64)

    # connections along x direction
    idx_col = idx[0:-1, :, :].flatten()
    idx_row = idx[1:, :, :].flatten()
    data = np.ones((nx-1)*ny*nz, dtype=np.int64)
    A_connection += sps.csc_matrix((data, (idx_row, idx_col)), shape=(n, n), dtype=np.int64)

    # connections along y direction
    idx_col = idx[:, 0:-1, :].flatten()
    idx_row = idx[:, 1:, :].flatten()
    data = np.ones(nx*(ny-1)*nz, dtype=np.int64)
    A_connection += sps.csc_matrix((data, (idx_row, idx_col)), shape=(n, n), dtype=np.int64)

    # connections along z direction
    idx_col = idx[:, :, 0:-1].flatten()
    idx_row = idx[:, :, 1:].flatten()
    data = np.ones(nx*ny*(nz-1), dtype=np.int64)
    A_connection += sps.csc_matrix((data, (idx_row, idx_col)), shape=(n, n), dtype=np.int64)

    return A_connection


def get_graph(n, domain_def):
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
    (n, labels) = csg.connected_components(csgraph=A_graph, directed=False, return_labels=True)

    # get the indices of the connected components
    connection_def = []
    for i in range(n):
        idx_local = np.flatnonzero(labels == i)
        idx_graph = idx[idx_local]
        connection_def.append(idx_graph)

    return connection_def
