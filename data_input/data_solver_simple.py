def get_data():
    data_solver = dict()

    data_solver["n"] = (4, 4, 3)
    data_solver["d"] = (1e-4, 2e-4, 1e-4)
    data_solver["r"] = (2, 2, 2)
    data_solver["ori"] = (0.0, 0.0, 0.0)
    data_solver["n_green"] = 25.0

    data_solver["conductor"] = {
        "pri": {"idx": [0, 3, 4, 8, 12, 13, 14, 15, 11, 7], "rho": 1.75e-8},
        "sec": {"idx": [32, 33, 34, 35, 39, 43, 47, 46, 45, 44, 40, 36], "rho": 8.77e-8},
    }
    data_solver["source"] = {
        "src": {"source_type": "current", "idx": [0], "I": +1.0, "G": 0.0},
        "sink": {"source_type": "voltage", "idx": [3], "V": +1.0, "R": 0.0},
        "short": {"source_type": "voltage", "idx": [45], "V": -1.0, "R": 0.0},
    }

    data_solver["freq"] = 10e6
    data_solver["solver_options"] = {"tol": 1e-6, "atol": 1e-12, "restart": 20, "maxiter": 100}
    data_solver["condition_options"] = {"check": True, "tolerance": 1e9, "accuracy": 2}

    return data_solver
