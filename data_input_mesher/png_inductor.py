import os


def get_data():
    # read the image
    path = os.path.dirname(__file__)
    path = os.path.join(path, "png_inductor")

    # init
    mesh_type = "png"
    data_mesher = dict()

    # voxel size
    data_mesher["d"] = (35e-6, 35e-6, 35e-6)
    data_mesher["r"] = (1, 1, 1)
    data_mesher["nx"] = 176
    data_mesher["ny"] = 160

    # domain colors
    data_mesher["domain_color"] = {
        "coil": [0, 0, 0, 255],
        "src": [255, 0, 0, 255],
        "sink": [0, 255, 0, 255],
    }

    # layer stack definition
    data_mesher["layer_stack"] = [
        {"n_add": 1, "filename": os.path.join(path, "return.png")},
        {"n_add": 6, "filename": os.path.join(path, "via.png")},
        {"n_add": 1, "filename": os.path.join(path, "coil.png")},
    ]

    return mesh_type, data_mesher
