"""
Different functions for extracting PyVista object from the voxel structure:
    - the complete voxel structure (uniform grid)
    - the structure containing non-empty voxels (unstructured grid)
    - the defined point cloud (polydata object)

For the viewer, create the objects and add the domain definition.

For the plotter, create the objects and add the solution:
    - material description (conductors and sources)
    - resistivity
    - potential
    - current density
    - loss/energy
    - magnetic field
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import numpy as np
import numpy.linalg as lna
from PyPEEC.lib_utils.error import RunError


def _get_biot_savart(pts, pts_src, J_src, vol):
    """
    Compute the magnetic field at a specified point.
    The field is created by many current densities.
    """

    # get the distance between the points and the voxels
    vec = pts-pts_src

    # get the norm of the distance
    nrm = lna.norm(vec, axis=1, keepdims=True)

    # compute the Biot-Savart contributions
    H_all = (vol/(4*np.pi))*(np.cross(J_src, vec, axis=1)/(nrm**3))

    # sum the contributions
    H_pts = np.sum(H_all, axis=0)

    return H_pts


def _get_magnetic_charge(pts, pts_src, Q_src, vol):
    # vacuum permeability
    mu = 4*np.pi*1e-7

    # get the distance between the points and the voxels
    vec = pts_src-pts

    # get the norm of the distance
    nrm = lna.norm(vec, axis=1, keepdims=True)

    # transform the charge into a vector
    Q_src = np.tile(np.array(Q_src), (3, 1)).transpose()

    # compute the Biot-Savart contributions
    H_all = (vol/(4*np.pi*mu))*((Q_src*vec)/(nrm**3))

    # sum the contributions
    H_pts = np.sum(H_all, axis=0)

    return H_pts


def _get_graph_component(idx, connection_def):
    # init the data with invalid data
    gra = np.zeros(len(idx), dtype=np.int64)

    # find to corresponding connected components
    for i, idx_graph in enumerate(connection_def):
        # find which indices are part of the connected component
        idx_ok = np.in1d(idx, idx_graph)

        # assign the component number to the corresponding indices
        gra[idx_ok] = i+1

    # check that everything was assigned
    if not np.all(gra):
        raise RunError("invalid graph: some voxels are not part of the graph")

    return gra


def get_viewer_domain(domain_def, connection_def):
    """
    Get the indices of the non-empty voxels.
    Assign a different scalar for each domain.
    Assign a different scalar for each connected component.
    """

    # init
    idx_v = np.empty(0, dtype=np.int64)
    dom_v = np.empty(0, dtype=np.int64)
    gra_v = np.empty(0, dtype=np.int64)

    # get the indices and colors
    counter = 1
    for tag, idx_tmp in domain_def.items():
        # assign the color (n different integer for each domain)
        dom_tmp = np.full(len(idx_tmp), counter, dtype=np.int64)

        # update the domain counter
        counter += 1

        # find the connected components corresponding to the indices
        gra_tmp = _get_graph_component(idx_tmp, connection_def)

        # append the indices and colors
        idx_v = np.append(idx_v, idx_tmp)
        dom_v = np.append(dom_v, dom_tmp)
        gra_v = np.append(gra_v, gra_tmp)

    return idx_v, dom_v, gra_v


def get_magnetic_field(d, idx_vc, idx_vm, J_vc, S_vm, coord_vox, data_point):
    """
    Compute the magnetic field for the provided points.
    The Biot-Savart law is used for te computation.
    """

    # extract the voxel volume
    vol = np.prod(d)

    # keep non-empty voxels
    pts_vc = coord_vox[idx_vc]
    pts_vm = coord_vox[idx_vm]

    # for each provided point, compute the magnetic field
    H_points = np.zeros((len(data_point), 3), dtype=np.complex128)
    for i, pts_tmp in enumerate(data_point):
        H_c = _get_biot_savart(pts_tmp, pts_vc, J_vc, vol)
        H_m = _get_magnetic_charge(pts_tmp, pts_vm, S_vm, vol)
        H_points[i, :] = H_c+H_m

    return H_points
