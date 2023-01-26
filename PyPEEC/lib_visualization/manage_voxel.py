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
import pyvista as pv
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


def _get_domain_tag(idx, counter):
    # assign the color (n different integer for each domain)
    dom = np.full(len(idx), counter, dtype=np.int64)

    # update the domain counter
    counter += 1

    return dom, counter


def get_grid(n, d, c):
    """
    Construct a PyVista uniform grid for the complete voxel structure.
    """

    # extract the voxel data
    (nx, ny, nz) = n
    (dx, dy, dz) = d
    (cx, cy, cz) = c

    # origin coordinate
    ox = cx-(nx*dx)/2
    oy = cy-(ny*dy)/2
    oz = cz-(nz*dz)/2

    # create a uniform grid for the complete structure
    grid = pv.UniformGrid()

    # set the array size and the voxel size
    grid.origin = (ox, oy, oz)
    grid.dimensions = (nx+1, ny+1, nz+1)
    grid.spacing = (dx, dy, dz)

    return grid


def get_voxel(grid, idx_v):
    """
    Construct a PyVista unstructured grid for the non-empty voxels.
    The indices of the non-empty vocels are provided.
    """

    # sort idx
    idx_v = np.sort(idx_v)

    # transform the uniform grid into an unstructured grid (keeping the non-empty voxels)
    voxel = grid.extract_cells(idx_v)

    return voxel


def get_point(voxel, data_point):
    """
    Construct a PyVista point cloud (polydata) with the defined points.
    The points cannot be located inside the non-empty voxels.
    """

    # cast the array with the coordinates
    data_point = np.array(data_point, dtype=np.float64)

    # create the point cloud
    point = pv.PolyData(data_point)

    # check that the points are not inside the grid
    surface = voxel.extract_surface()
    selection = point.select_enclosed_points(surface, tolerance=0.0, check_surface=False)
    mask = selection['SelectedPoints'].view(bool)
    if np.any(mask):
        raise RunError("invalid points: points should not be located inside the non-empty voxels.")

    return point


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
        (dom_tmp, counter) = _get_domain_tag(idx_tmp, counter)

        # find the connected components corresponding to the indices
        gra_tmp = _get_graph_component(idx_tmp, connection_def)

        # append the indices and colors
        idx_v = np.append(idx_v, idx_tmp)
        dom_v = np.append(dom_v, dom_tmp)
        gra_v = np.append(gra_v, gra_tmp)

    return idx_v, dom_v, gra_v


def get_magnetic_field(d, idx_v, J_v, voxel_point, data_point):
    """
    Compute the magnetic field for the provided points.
    The Biot-Savart law is used for te computation.
    """

    # extract the voxel volume
    vol = np.prod(d)

    # keep non-empty voxels
    pts_v = voxel_point[idx_v]

    # for each provided point, compute the magnetic field
    H_points = np.zeros((len(data_point), 3), dtype=np.complex128)
    for i, pts_tmp in enumerate(data_point):
        H_points[i, :] = _get_biot_savart(pts_tmp, pts_v, J_v, vol)

    return H_points


def set_viewer_domain(voxel, idx_v, dom_v, gra_v):
    """
    Add the domains to the unstructured grid.
    Add the connected components to the unstructured grid.
    A fake scalar field is used to encode the domains and connected components.
    """

    # sort idx
    idx_sort = np.argsort(idx_v)
    dom_v = dom_v[idx_sort]
    gra_v = gra_v[idx_sort]

    # assign the extract data to the geometry
    voxel["domain"] = dom_v
    voxel["connection"] = gra_v

    return voxel


def set_plotter_voxel_material(voxel, idx_v, idx_src_c, idx_src_v):
    """
    Add the material description to the unstructured grid.
    The following fake scalar field encoding is used:
        - 0: conducting voxels
        - 1: current source voxels
        - 2: voltage source voxels
    """

    # assign conductors
    data = np.zeros(len(idx_v), dtype=np.float64)

    # get the local source indices
    idx_src_c_local = np.flatnonzero(np.in1d(idx_v, idx_src_c))
    idx_src_v_local = np.flatnonzero(np.in1d(idx_v, idx_src_v))

    # assign the voltage and current sources
    data[idx_src_c_local] = 1
    data[idx_src_v_local] = 2

    # sort idx
    idx_sort = np.argsort(idx_v)
    data = data[idx_sort]

    # assign the extract data to the geometry
    voxel["material"] = data

    return voxel


def set_plotter_voxel_data(voxel, idx_v, rho_v, V_v, J_v, P_v):
    """
    Add the different variables to the unstructured grid:
        - resistivity (scalar field, input variable)
        - potential (scalar field, solved variable)
        - current density (scalar and vector fields, solved variable)
        - loss (scalar field, solved variable)
    """

    # sort idx
    idx_s = np.argsort(idx_v)

    # reorder variables
    rho_v = rho_v[idx_s]
    V_v = V_v[idx_s]
    P_v = P_v[idx_s]
    J_v = J_v[idx_s,]

    # assign data
    voxel["rho"] = rho_v
    voxel["P"] = P_v

    # assign potential
    voxel["V_re"] = np.real(V_v)
    voxel["V_im"] = np.imag(V_v)
    voxel["V_abs"] = np.abs(V_v)

    # assign the current density norm
    voxel["J_norm_abs"] = lna.norm(J_v, axis=1)
    voxel["J_norm_re"] = lna.norm(np.real(J_v), axis=1)
    voxel["J_norm_im"] = lna.norm(np.imag(J_v), axis=1)

    # assign the current density direction
    voxel["J_vec_re"] = np.real(J_v)
    voxel["J_vec_im"] = np.imag(J_v)

    return voxel


def set_plotter_magnetic_field(point, H_point):
    """
    Add the magnetic field (scalar and vector fields, current density) to the point cloud.
    The norm (scalar field) and the direction (vector field) are added.
    """

    # compute the norm
    point["H_norm_abs"] = lna.norm(H_point, axis=1)
    point["H_norm_re"] = lna.norm(np.real(H_point), axis=1)
    point["H_norm_im"] = lna.norm(np.imag(H_point), axis=1)

    # compute the direction
    point["H_vec_re"] = np.real(H_point)
    point["H_vec_im"] = np.imag(H_point)

    return point
