def get_data():
    # init
    mesh_type = "voxel"
    data_mesher = dict()
    data_resampling = {"use_resampling": True, "n_resampling": (1, 1, 1)}

    # add data
    data_mesher["n"] = (2, 1, 3)
    data_mesher["d"] = (0.5e-2, 1e-2, 1e-2)
    data_mesher["domain_def"] = {
        "cond": [2, 3],
        "src": [0, 1],
        "sink": [4, 5],
    }

    return mesh_type, data_mesher, data_resampling
