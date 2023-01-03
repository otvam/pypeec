def get_data_init():
    data_init = dict()

    data_init["nx"] = 4
    data_init["ny"] = 4
    data_init["nz"] = 3

    data_init["dx"] = 1e-4
    data_init["dy"] = 2e-4
    data_init["dz"] = 1e-4

    data_init["n_min_center"] = 25

    return data_init


def get_data_solve():
    data_solve = dict()

    conductor = []
    conductor.append({"idx": [0, 3, 4, 8, 12, 13, 14, 15, 11, 7], "rho": 1.7544e-08})
    conductor.append({"idx": [32, 33, 34, 35, 39, 43, 47, 46, 45, 44, 40, 36], "rho": 8.7720e-08})

    src_current = []
    src_current.append({"tag": "src", "idx": [0], "value": +1})

    src_voltage = []
    src_voltage.append({"tag": "sink", "idx": [3], "value": +1})
    src_voltage.append({"tag": "short", "idx": [45], "value": -1})

    solver_options = {"tol": 1e-5, "atol": 1e-12, "restart": 20, "maxiter": 100}

    data_solve["freq"] = 10e6
    data_solve["solver_options"] = solver_options
    data_solve["conductor"] = conductor
    data_solve["src_current"] = src_current
    data_solve["src_voltage"] = src_voltage

    return data_solve
