def get_data():
    # init
    mesh_type = "voxel"
    data_mesher = dict()
    data_resampling = {"use_resampling": True, "n_resampling": (1, 1, 1)}

    # add data
    data_mesher["n"] = (4, 4, 3)
    data_mesher["d"] = (1e-4, 2e-4, 1e-4)
    data_mesher["domain_def"] = {
        "pri": [4, 8, 12, 13, 14, 15, 11, 7],
        "sec": [32, 33, 34, 35, 39, 43, 47, 46, 44, 40, 36],
        "src": [0],
        "sink": [3],
        "short": [45],
    }

    return mesh_type, data_mesher, data_resampling
