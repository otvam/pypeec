def get_data():
    data_problem = dict()
    data_problem["n_green"] = 25.0
    data_problem["freq"] = 0.0
    data_problem["solver_options"] = {"tol": 1e-6, "atol": 1e-12, "restart": 20, "maxiter": 100}
    data_problem["condition_options"] = {"check": True, "tolerance": 1e9, "accuracy": 2}
    data_problem["conductor_def"] = {
        "cond": {"domain": ["cond", "src", "sink"], "rho": 1e-2},
    }
    data_problem["source_def"] = {
        "src": {"domain": ["src"], "source_type": "current", "I": 1.0, "G": 0.5},
        "sink": {"domain": ["sink"], "source_type": "voltage", "V": 0.0, "R": 2.0},
    }

    return data_problem
