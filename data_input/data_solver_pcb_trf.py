def _add_image(conductor, source, n, data):

    return conductor, source


def get_data():
    n = (176, 160, 20)
    d = (50e-6, 50e-6, 50e-6)
    r = (1, 1, 1)
    ori = (0, 0, 0)
    d_green = 1e-3
    freq = 1e6
    solver_options = {"tol": 1e-6, "atol": 1e-12, "restart": 20, "maxiter": 100}
    condition_options = {"check": True, "tolerance": 1e9, "accuracy": 2}

    # init geometry description
    conductor = {}
    source = {}

    # stack
    data = {
        "idx_z": [0],
        "filename": "pcb_trf/return.png",
        "conductor": {
            "c_1_return": {"color": [[255, 255, 255]], "rho": 1.7544e-08},
        },
        "source": {
            "src_1": {"color": [[255, 255, 255]], "source_type": "current", "value": +1},
        },
    }
    (conductor, source), _add_image(conductor, source, n, data)

    # assign results
    data_solver = {
        "n": n,
        "d": d,
        "r": r,
        "ori": ori,
        "d_green": d_green,
        "conductor": conductor,
        "source": source,
        "freq": freq,
        "solver_options": solver_options,
        "condition_options": condition_options,
    }

    return data_solver


