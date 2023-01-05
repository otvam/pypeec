import sys
import pickle

from main import solver
import data_trf

if __name__ == '__main__':
    # get data
    data_solver = data_trf.get_data()

    # call solver
    (status, data_res) = solver.run(data_solver)

    # check data
    assert status, "invalid simulation"

    # save results
    with open('data_trf.pck', 'wb') as fid:
        pickle.dump((status, data_res), fid)

    # exit
    status = int(status == False)
    sys.exit(status)
