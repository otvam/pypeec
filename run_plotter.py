import data_plotter
from main import plotter
import pickle


# get data
data_plotter = data_plotter.get_data_plotter()

# load data
with open('data_trf.pck', 'rb') as fid:
    (status, data_res) = pickle.load(fid)

# check data
assert status, "invalid simulation"

# call plotter
plotter.run(data_res, data_plotter)
