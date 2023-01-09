def get_data():
    data_solver = dict()

    data_solver["n"] = (2, 1, 3)
    data_solver["d"] = (0.5e-2, 1e-2, 1e-2)
    data_solver["r"] = (1, 1, 1)
    data_solver["ori"] = (0, 0, 0)
    data_solver["d_green"] = 20e-4

    data_solver["conductor"] = {
        "cond": {"idx": [0, 1, 2, 3, 4, 5], "rho": 1e-2},
    }
    data_solver["source"] = {
        "src": {"source_type": "current", "idx": [0, 1], "I": 1.0, "G": 0.5},
        "sink": {"source_type": "voltage", "idx": [4, 5], "V": 0.0, "R": 2.0},
    }

    data_solver["freq"] = 0
    data_solver["solver_options"] = {"tol": 1e-6, "atol": 1e-12, "restart": 20, "maxiter": 100}
    data_solver["condition_options"] = {"check": True, "tolerance": 1e9, "accuracy": 2}

    return data_solver
