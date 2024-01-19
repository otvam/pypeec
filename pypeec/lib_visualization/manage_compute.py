"""
Different functions for post-processing the solution before plotting.
For the viewer, extract the domain description and the graph components.
For the plotter, extract the material description.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import numpy as np
from pypeec import config
from pypeec.error import RunError

# get config
NP_TYPES = config.NP_TYPES


def _get_graph_component(idx, connection_def):
    """
    Find the connected components for a specific domain.
    Assign a different scalar for each connected component.
    """

    # init the data with invalid data
    if len(connection_def) == 0:
        tag = np.ones(len(idx), dtype=NP_TYPES.INT)
    else:
        tag = np.zeros(len(idx), dtype=NP_TYPES.INT)

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


def get_geometry_tag(domain_def, connection_def):
    """
    Get the indices of the non-empty voxels.
    Assign a different integer for each domain.
    Assign a different integer for each connected component.
    """

    # init
    idx = np.empty(0, dtype=NP_TYPES.INT)
    domain = np.empty(0, dtype=NP_TYPES.INT)
    connection = np.empty(0, dtype=NP_TYPES.INT)

    # get the indices and colors
    counter = 1
    for tag, idx_tmp in domain_def.items():
        # assign the color (n different integer for each domain)
        domain_tmp = np.full(len(idx_tmp), counter, dtype=NP_TYPES.INT)

        # find the connected components corresponding to the indices
        connection_tmp = _get_graph_component(idx_tmp, connection_def)

        # append the indices and colors
        idx = np.append(idx, idx_tmp)
        domain = np.append(domain, domain_tmp)
        connection = np.append(connection, connection_tmp)

        # update the domain counter
        counter += 1

    return idx, domain, connection


def get_material_tag(idx_vc, idx_vm, idx_src_c, idx_src_v):
    """
    Assign a different integer for the material and source types.
    """

    # get the indices
    idx = np.concatenate((idx_vc, idx_vm))

    # find position
    idx_vc_local = np.in1d(idx, idx_vc)
    idx_vm_local = np.in1d(idx, idx_vm)
    idx_src_c_local = np.in1d(idx, idx_src_c)
    idx_src_v_local = np.in1d(idx, idx_src_v)

    # init the material
    material = np.empty(len(idx), dtype=NP_TYPES.INT)

    # assign the voltage and current sources
    material[idx_vc_local] = 1
    material[idx_vm_local] = 2
    material[idx_src_c_local] = 3
    material[idx_src_v_local] = 4

    return idx, material


