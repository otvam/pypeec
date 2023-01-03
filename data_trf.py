def get_data_solver():
    data_solver = dict()

    conductor = []
    conductor.append({"idx": [0, 3, 4, 8, 12, 13, 14, 15, 11, 7], "rho": 1.7544e-08})
    conductor.append({"idx": [32, 33, 34, 35, 39, 43, 47, 46, 45, 44, 40, 36], "rho": 8.7720e-08})

    src_current = []
    src_current.append({"tag": "src", "idx": [0], "value": +1})

    src_voltage = []
    src_voltage.append({"tag": "sink", "idx": [3], "value": +1})
    src_voltage.append({"tag": "short", "idx": [45], "value": -1})

    solver_options = {"tol": 1e-5, "atol": 1e-12, "restart": 20, "maxiter": 100}

    data_solver["n"] = (4, 4, 3)
    data_solver["d"] = (1e-4, 2e-4, 1e-4)
    data_solver["n_green_simplify"] = 25

    data_solver["freq"] = 10e6
    data_solver["solver_options"] = solver_options

    data_solver["conductor"] = conductor
    data_solver["src_current"] = src_current
    data_solver["src_voltage"] = src_voltage

    return data_solver
