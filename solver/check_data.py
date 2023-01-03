import numpy as np


def __check_conductor(idx_v, conductor):
    for dat_tmp in conductor:
        idx = dat_tmp["idx"]
        rho = dat_tmp["rho"]

        assert np.isscalar(rho), "conductor resistivity should be a scalar"
        assert np.isreal(rho), "conductor resistivity should be real"
        assert rho > 0, "conductor resistivity should be greater than zero"

        idx_v = np.append(idx_v, np.array(idx))

    return idx_v


def __check_src(idx_src, tag_src, src):
    for dat_tmp in src:
        tag = dat_tmp["tag"]
        idx = dat_tmp["idx"]
        value = dat_tmp["value"]

        assert np.isscalar(value), "source value should be a scalar"
        assert isinstance(tag, str), "source name should be a string"

        tag_src.append(tag)
        idx_src = np.append(idx_src, np.array(idx))

    return idx_src, tag_src


def check_voxel(data_solver):
    # extract field
    n = data_solver["n"]
    d = data_solver["d"]
    n_green_simplify = data_solver["n_green_simplify"]

    # check size
    assert len(n) == 3, "invalid voxel size"
    assert len(d) == 3, "invalid voxel size"

    # extract the voxel data
    (nx, ny, nz) = n
    (dx, dy, dz) = d

    # check value
    assert nx >= 1, "number of voxels cannot be smaller than one"
    assert ny >= 1, "number of voxels cannot be smaller than one"
    assert nz >= 1, "number of voxels cannot be smaller than one"
    assert dx > 0, "voxel dimension cannot be zero or smaller"
    assert dy > 0, "voxel dimension cannot be zero or smaller"
    assert dz > 0, "voxel dimension cannot be zero or smaller"
    assert n_green_simplify > 0, "voxel distance to simplify the green function cannot be zero of smaller"

    return n, d, n_green_simplify


def check_solver(data_solver):
    # extract field
    freq = data_solver["freq"]
    solver_options = data_solver["solver_options"]

    # check frequency
    assert freq >= 0, "frequency cannot be negative"

    # check solver options
    assert isinstance(solver_options, dict), "solver options should be a dict"
    assert solver_options["tol"] > 0, "solver relative tolerance should be greater than zero"
    assert solver_options["atol"] > 0, "solver absolute tolerance should be greater than zero"
    assert solver_options["restart"] >= 1, "number of iterations between restarts should be greater than zero"
    assert solver_options["restart"] >= 1, "number of restart cycles should be greater than zero"

    return freq, solver_options


def check_problem(data_solver):
    # extract field
    conductor = data_solver["conductor"]
    src_current = data_solver["src_current"]
    src_voltage = data_solver["src_voltage"]
    n = data_solver["n"]

    # extract the voxel data
    (nx, ny, nz) = n
    n = nx*ny*nz

    # check type
    assert isinstance(conductor, list), "solver options should be a dict"
    assert isinstance(src_current, list), "solver options should be a dict"
    assert isinstance(src_voltage, list), "solver options should be a dict"

    # check the conductor
    idx_v = np.array([], dtype=np.int64)
    idx_src = np.array([], dtype=np.int64)
    tag_src = []

    # find the indices and tags
    idx_v = __check_conductor(idx_v, conductor)
    (idx_src, tag_src) = __check_src(idx_src, tag_src, src_current)
    (idx_src, tag_src) = __check_src(idx_src, tag_src, src_voltage)

    # check for unicity
    assert len(np.unique(idx_v)) == len(idx_v), "conductor indices should be unique"
    assert len(np.unique(idx_src)) == len(idx_src), "source indices should be unique"
    assert len(np.unique(tag_src)) == len(tag_src), "source tag should be unique"

    # check for indices range
    assert np.all(idx_v >= 0) and np.all(idx_v < n) , "conductor indices should belong to the voxel structure"
    assert np.all(idx_src >= 0) and np.all(idx_src < n) , "source indices should belong to the voxel structure"

    # check that the terminal indices are conductor indices
    assert np.all(np.isin(idx_src, idx_v)), "source indices are not included in conductor indices"

    return conductor, src_current, src_voltage