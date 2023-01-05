import sys
import pickle

from main import plotter
import data_plotter

if __name__ == '__main__':
    # get data
    data_plotter = data_plotter.get_data()

    # load data
    with open('data_trf.pck', 'rb') as fid:
        (status, data_res) = pickle.load(fid)

    # check data
    assert status, "invalid simulation"

    # call plotter
    status = plotter.run(data_res, data_plotter)

    # exit
    sys.exit(status)
