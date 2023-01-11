def get_data():
    data_solver = dict()

    data_solver["n"] = (1, 1, 3)
    data_solver["d"] = (1e-2, 1e-2, 1e-2)
    data_solver["r"] = (1, 1, 1)
    data_solver["ori"] = (0.0, 0.0, 0.0)
    data_solver["n_green"] = 25.0

    data_solver["conductor"] = {
        "cond_1": {"idx": [0, 2], "rho": 1e-2},
        "cond_2": {"idx": [1], "rho": 2e-2},
    }
    data_solver["source"] = {
        "src": {"source_type": "current", "idx": [0], "I": 1.0, "G": 0.0},
        "sink": {"source_type": "voltage", "idx": [2], "V": 0.0, "R": 0.0},
    }

    data_solver["freq"] = 0
    data_solver["solver_options"] = {"tol": 1e-6, "atol": 1e-12, "restart": 20, "maxiter": 100}
    data_solver["condition_options"] = {"check": True, "tolerance": 1e9, "accuracy": 2}

    return data_solver
