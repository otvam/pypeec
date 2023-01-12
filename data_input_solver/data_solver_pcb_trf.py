import os
import numpy as np
import imageio.v3 as iio


def _get_idx_image(nx, ny, img, color):
    # check image
    assert img.shape == (nx, ny, 4), "invalid image size"

    # init idx
    idx_img = np.array([], dtype=np.int64)

    # get the indices
    for color_tmp in color:
        # get the color vector
        color_tmp = np.array(color_tmp)
        color_tmp = np.expand_dims(color_tmp, axis=(0, 1))
        assert color_tmp.shape == (1, 1, 4), "invalid image size"

        # find the color
        idx_tmp = np.all(img == color_tmp, axis=2)
        idx_tmp = idx_tmp.flatten(order="F")
        idx_tmp = np.flatnonzero(idx_tmp)

        # add the indices to the array
        idx_img = np.append(idx_img, idx_tmp)

    return idx_img


def _get_idx_voxel(nx, ny, nz, n_add, idx_img):
    # init idx
    idx = np.array([], dtype=np.int64)

    # convert image indices into voxel indices
    for n_tmp in range(n_add):
        # convert indices
        idx_tmp = (nz+n_tmp)*nx*ny+idx_img

        # add the indices to the array
        idx = np.append(idx, idx_tmp)

    return idx


def _get_image(filename):
    img = iio.imread(filename)
    img = np.swapaxes(img, 0, 1)
    img = np.flip(img, axis=1)

    return img


def _get_color_indices(data, nx, ny, nz, n_add, img, data_color):
    for tag_tmp, color_tmp in data_color.items():
        # get the indices
        idx_img = _get_idx_image(nx, ny, img, color_tmp)
        idx_add = _get_idx_voxel(nx, ny, nz, n_add, idx_img)

        # add the indices
        idx = data[tag_tmp]["idx"]
        idx = np.array(idx, dtype=np.int64)
        idx = np.append(idx, idx_add)
        data[tag_tmp]["idx"] = idx

    return data


def _add_layer(conductor, source, nx, ny, nz, data):
    # extract the data
    n_add = data["n_add"]
    filename = data["filename"]
    conductor_color = data["conductor_color"]
    source_color = data["source_color"]

    # add the indices
    if filename is not None:
        # read the image
        path = os.path.dirname(__file__)
        filename = os.path.join(path, filename)
        img = _get_image(filename)

        # add the indices
        conductor = _get_color_indices(conductor, nx, ny, nz, n_add, img, conductor_color)
        source = _get_color_indices(source, nx, ny, nz, n_add, img, source_color)

    # update the layer stack
    nz += n_add

    return nz, conductor, source


def get_data():
    # problem parameters
    nx = 176
    ny = 160
    d = (35e-6, 35e-6, 35e-6)
    r = (1, 1, 1)
    n_green = 25.0
    freq = 1e6
    solver_options = {"tol": 1e-6, "atol": 1e-12, "restart": 20, "maxiter": 100}
    condition_options = {"check": True, "tolerance": 1e9, "accuracy": 2}

    # init the conductors and sources (without the indices)
    conductor = {
        "pri": {"idx": [], "rho": 1.75e-8},
        "sec": {"idx": [], "rho": 1.75e-8},
    }
    source = {
        "pri_src": {"source_type": "current", "idx": [], "I": 1.0, "G": 0.01},
        "pri_sink": {"source_type": "voltage", "idx": [], "V": 0.0, "R": 0.01},
        "sec_src": {"source_type": "current", "idx": [], "I": 0.0, "G": 0.01},
        "sec_sink": {"source_type": "voltage", "idx": [], "V": 0.0, "R": 0.01},
    }

    # color legends
    color_conductor = [[0, 0, 0, 255], [0, 255, 0, 255], [255, 0, 0, 255]]
    color_sink = [[0, 255, 0, 255]]
    color_source = [[255, 0, 0, 255]]

    # layer stack definition
    data = [
        {
            "n_add": 1,
            "filename": "png_inductor/return.png",
            "conductor_color": {"pri": color_conductor},
            "source_color": {"pri_sink": color_sink}
        },
        {
            "n_add": 6,
            "filename": "png_inductor/via.png",
            "conductor_color": {"pri": color_conductor},
            "source_color": {}
        },
        {
            "n_add": 1,
            "filename": "png_inductor/coil.png",
            "conductor_color": {"pri": color_conductor},
            "source_color": {"pri_src": color_source}
        },
        {
            "n_add": 6,
            "filename": None,
            "conductor_color": {},
            "source_color": {}
        },
        {
            "n_add": 1,
            "filename": "png_inductor/coil.png",
            "conductor_color": {"sec": color_conductor},
            "source_color": {"sec_src": color_source}
        },
        {
            "n_add": 6,
            "filename": "png_inductor/via.png",
            "conductor_color": {"sec": color_conductor},
            "source_color": {}
        },
        {
            "n_add": 1,
            "filename": "png_inductor/return.png",
            "conductor_color": {"sec": color_conductor},
            "source_color": {"sec_sink": color_sink}
        },
    ]

    # init stack
    nz = 0

    # add the layers
    for dat_tmp in data:
        (nz, conductor, source) = _add_layer(conductor, source, nx, ny, nz, dat_tmp)

    # get voxel size
    n = (nx, ny, nz)

    # assign results
    data_solver = {
        "n": n,
        "d": d,
        "r": r,
        "n_green": n_green,
        "conductor": conductor,
        "source": source,
        "freq": freq,
        "solver_options": solver_options,
        "condition_options": condition_options,
    }

    return data_solver
