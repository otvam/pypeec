def get_data():
    data_solver = dict()

    conductor = {
        "pri": {"idx": [0, 3, 4, 8, 12, 13, 14, 15, 11, 7], "rho": 1.7544e-08},
        "sec": {"idx": [32, 33, 34, 35, 39, 43, 47, 46, 45, 44, 40, 36], "rho": 8.7720e-08},
    }

    source = {
        "src": {"source_type": "current", "idx": [0], "value": +1},
        "sink": {"source_type": "voltage", "idx": [3], "value": +1},
        "short": {"source_type": "voltage", "idx": [45], "value": -1},
    }

    data_solver["n"] = (4, 4, 3)
    data_solver["d"] = (1e-4, 2e-4, 1e-4)
    data_solver["r"] = (5, 5, 5)
    data_solver["ori"] = (0, 0, 0)
    data_solver["d_green_simplify"] = 20e-4

    data_solver["freq"] = 10e6
    data_solver["solver_options"] = {"tol": 1e-6, "atol": 1e-12, "restart": 20, "maxiter": 100}
    data_solver["condition_options"] = {"check": True, "tolerance": 1e9, "accuracy": 2}

    data_solver["conductor"] = conductor
    data_solver["source"] = source

    return data_solver
