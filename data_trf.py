def get_data_init():
    data_init = dict()

    data_init["nx"] = 4
    data_init["ny"] = 4
    data_init["nz"] = 3

    data_init["dx"] = 1e-4
    data_init["dy"] = 2e-4
    data_init["dz"] = 1e-4

    data_init["n_min_center"] = 4

    return data_init


def get_data_solve():
    data_solve = dict()

    conductor = []
    conductor.append({"idx": [1, 4, 5, 9, 13, 14, 15, 16, 12, 8], "rho": 1.7544e-08})
    conductor.append({"idx": [33, 34, 35, 36, 40, 44, 48, 47, 46, 45, 41, 37], "rho": 8.7720e-08})

    src_current = []
    src_current.append({"tag": "src", "idx": [1], "value": +1})

    src_voltage = []
    src_voltage.append({"tag": "sink", "idx": [4], "value": +1})
    src_voltage.append({"tag": "short", "idx": [46], "value": -1})

    data_solve["conductor"] = conductor
    data_solve["src_current"] = src_current
    data_solve["src_voltage"] = src_voltage

    return data_solve
