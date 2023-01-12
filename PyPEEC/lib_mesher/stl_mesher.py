import numpy as np
import pyvista as pv


def _get_grid(n, d, pts_min):
    """
    Construct a PyVista grid from the voxel structure.
    The complete voxel geometry is represented with a PyVista uniform grid.
    """

    # create a uniform grid for the complete structure
    grid = pv.UniformGrid()

    # set the array size and the voxel size
    grid.origin = pts_min
    grid.dimensions = n+1
    grid.spacing = d

    # add the indices for tracking after voxelization
    grid["idx"] = np.arange(np.prod(n), dtype=np.int64)

    # cast is required for voxelization
    grid = grid.cast_to_unstructured_grid()

    return grid


def get_voxelize(grid, mesh):
    # voxelize
    selection = grid.select_enclosed_points(mesh, tolerance=0.0, check_surface=True)

    # create a boolean mask
    mask = selection.point_data['SelectedPoints'].view(bool)

    # extract the voxels
    geom = grid.extract_points(mask)

    # get the indices of the voxels
    idx = geom["idx"]

    return idx


def _get_idx_stl(grid, mesh_stl):
    # init
    domain_def = dict()

    # load the STL files
    for tag, mesh in mesh_stl.items():
        # voxelize and get the indices
        idx = get_voxelize(grid, mesh)

        # assign the indices to the domain
        domain_def[tag] = idx

    return domain_def


def _get_load_stl(domain_stl):
    # init mesh dict
    mesh_stl = dict()
    coord_min = np.full(3, +np.inf, dtype=np.float64)
    coord_max = np.full(3, -np.inf, dtype=np.float64)

    # load the STL files
    for tag, filename in domain_stl.items():
        # load the STL
        mesh = pv.read(filename)

        # find the bounds
        (x_min, x_max, y_min, y_max, z_min, z_max) = mesh.bounds
        tmp_min = np.array((x_min, y_min, z_min), dtype=np.float64)
        tmp_max = np.array((x_max, y_max, z_max), dtype=np.float64)

        # update the bounds
        coord_min = np.minimum(coord_min, tmp_min)
        coord_max = np.maximum(coord_max, tmp_max)

        # assign the mesh
        mesh_stl[tag] = mesh

    return mesh_stl, coord_min, coord_max


def _get_solve_overlap(domain_def, domain_add, domain_sub):
    # get the indices
    idx_add = domain_def[domain_add]
    idx_sub = domain_def[domain_sub]

    # resolve the conflict
    idx_sub = np.setdiff1d(idx_sub, idx_add)

    # update the domain indices
    domain_def[domain_sub] = idx_sub

    return domain_def


def get_mesh(n, pts_min, pts_max, domain_stl):
    # load the mesh and get the bounds
    (mesh_stl, coord_min, coord_max) = _get_load_stl(domain_stl)

    # cast to array
    n = np.array(n, np.int64)
    pts_min = np.array(pts_min, np.float64)
    pts_max = np.array(pts_max, np.float64)

    # update the bounds
    pts_min = np.array(pts_min, np.float64)
    pts_max = np.array(pts_max, np.float64)
    idx_replace_min = np.isnan(pts_min)
    idx_replace_max = np.isnan(pts_max)
    pts_min[idx_replace_min] = coord_min[idx_replace_min]
    pts_max[idx_replace_max] = coord_max[idx_replace_max]

    # extract the voxel size
    d = (pts_max-pts_min)/n

    # get the uniform grid
    grid = _get_grid(n, d, pts_min)

    # voxelize the meshes and get the indices
    domain_def = _get_idx_stl(grid, mesh_stl)

    # cast back to tuple
    d = tuple(d.tolist())

    return d, domain_def


def get_conflict(domain_def, domain_conflict):

    for dat_tmp in domain_conflict:
        # extract data
        domain_add = dat_tmp["domain_add"]
        domain_sub = dat_tmp["domain_sub"]

        # solve the conflict
        domain_def = _get_solve_overlap(domain_def, domain_add, domain_sub)

    # assemble all the indices
    idx_all = np.array([], dtype=np.int64)
    for idx in domain_def.values():
        idx_all = np.append(idx_all, idx)

    # check that conflicts are resolved
    if not (len(np.unique(idx_all)) == len(idx_all)):
        raise ValueError("domain indices should be unique")

    return domain_def