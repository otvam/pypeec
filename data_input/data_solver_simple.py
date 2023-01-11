def get_data_voxel():
    data_voxel = dict()

    data_voxel["n"] = (4, 4, 3)
    data_voxel["d"] = (1e-4, 2e-4, 1e-4)
    data_voxel["ori"] = (0.0, 0.0, 0.0)

    data_voxel["domain_def"] = {
        "pri": [4, 8, 12, 13, 14, 15, 11, 7],
        "sec": [32, 33, 34, 35, 39, 43, 47, 46, 44, 40, 36],
        "src": [0],
        "sink": [3],
        "short": [45],
    }

    return data_voxel


def get_data_problem():
    data_problem = dict()

    data_problem["conductor_def"] = {
        "pri": {"domain": ["src", "sink", "pri"], "rho": 1.75e-8},
        "sec": {"domain": ["sec"], "rho": 8.77e-8},
    }
    data_problem["source_def"] = {
        "src": {"domain": ["src"], "source_type": "current", "I": +1.0, "G": 0.0},
        "sink": {"domain": ["sink"], "source_type": "voltage", "V": +1.0, "R": 0.0},
        "short": {"domain": ["short"], "source_type": "voltage", "V": -1.0, "R": 0.0},
    }

    data_problem["n_green"] = 25.0
    data_problem["freq"] = 10e6
    data_problem["solver_options"] = {"tol": 1e-6, "atol": 1e-12, "restart": 20, "maxiter": 100}
    data_problem["condition_options"] = {"check": True, "tolerance": 1e9, "accuracy": 2}

    return data_problem
