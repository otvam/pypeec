import os


def get_data():
    # read the image
    path = os.path.dirname(__file__)
    path = os.path.join(path, "stl_inductor")

    # init
    mesh_type = "stl"
    data_mesher = dict()
    data_resampling = {"use_resampling": True, "n_resampling": (1, 1, 1)}

    # voxel size
    data_mesher["n"] = (150, 150, 25)
    data_mesher["pts_min"] = (None, None, None)
    data_mesher["pts_max"] = (None, None, None)

    # domain STLs
    data_mesher["domain_stl"] = {
        "coil": os.path.join(path, "coil.stl"),
        "src": os.path.join(path, "src.stl"),
        "sink": os.path.join(path, "sink.stl"),
    }
    data_mesher["domain_conflict"] = [
        {"domain_sub": "coil", "domain_add": "src"},
        {"domain_sub": "coil", "domain_add": "sink"},
    ]

    return mesh_type, data_mesher, data_resampling
