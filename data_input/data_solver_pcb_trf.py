import imageio.v3 as iio
import numpy as np


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


def _get_idx_voxel(nx, ny, nz, idx_z, idx_img):
    # init idx
    idx = np.array([], dtype=np.int64)

    # convert image indices into voxel indices
    for idx_tmp in idx_z:
        # check size
        assert (idx_tmp >= 0) and (idx_tmp < nz), "invalid image size"

        # convert indices
        idx_tmp = idx_tmp*nx*ny+idx_img

        # add the indices to the array
        idx = np.append(idx, idx_tmp)

    return idx


def _get_image(filename):
    img = iio.imread(filename)
    img = np.swapaxes(img, 0, 1)
    img = np.flip(img, axis=1)

    return img

def _add_layer(conductor, source, n, data):
    # extract the data
    idx_z = data["idx_z"]
    filename = data["filename"]
    conductor_color = data["conductor_color"]
    source_color = data["source_color"]

    # extract the voxel data_output
    (nx, ny, nz) = n

    # read the image
    img = _get_image(filename)

    # add conductor
    for tag, dat_tmp in conductor_color.items():
        # get the data
        color = dat_tmp["color"]
        rho = dat_tmp["rho"]

        # get the indices
        idx_img = _get_idx_image(nx, ny, img, color)
        idx = _get_idx_voxel(nx, ny, nz, idx_z, idx_img)

        # add the conductor
        conductor[tag] = {"idx": idx, "rho": rho}

    # add conductor
    for tag, dat_tmp in source_color.items():
        color = dat_tmp["color"]
        source_type = dat_tmp["source_type"]
        value = dat_tmp["value"]

        # get the indices
        idx = _get_idx_image(nx, ny, img, color)
        idx = _get_idx_voxel(nx, ny, nz, idx_z, idx)

        # add the source
        conductor[tag] = {"idx": idx, "source_type": source_type, "value": value}

    return conductor, source


def get_data():
    n = (176, 160, 20)
    d = (50e-6, 50e-6, 50e-6)
    r = (1, 1, 1)
    ori = (0, 0, 0)
    d_green = 1e-3
    freq = 1e6
    solver_options = {"tol": 1e-6, "atol": 1e-12, "restart": 20, "maxiter": 100}
    condition_options = {"check": True, "tolerance": 1e9, "accuracy": 2}

    # init geometry description
    conductor = {}
    source = {}

    # color
    color_conductor = [[0, 0, 0, 255], [0, 255, 0, 255], [255, 0, 0, 255]]
    color_sink = [[0, 0, 0, 255]]
    color_source = [255, 0, 0, 255]

    # stack
    data = {
        "idx_z": [0],
        "filename": "pcb_trf/return.png",
        "conductor_color": {
            "c_1_return": {"color": color_conductor, "rho": 1.7544e-08},
        },
        "source_color": {
            "src_1": {"color": color_sink, "source_type": "voltage", "value": 0},
        },
    }
    (conductor, source), _add_layer(conductor, source, n, data)

    # assign results
    data_solver = {
        "n": n,
        "d": d,
        "r": r,
        "ori": ori,
        "d_green": d_green,
        "conductor": conductor,
        "source": source,
        "freq": freq,
        "solver_options": solver_options,
        "condition_options": condition_options,
    }

    return data_solver


get_data()