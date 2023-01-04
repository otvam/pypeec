import data_trf
from main import solver
import pickle

data_solver = data_trf.get_data_solver()

data_res = solver.run(data_solver)

with open('data_trf.pck', 'wb') as fid:
    pickle.dump(data_res, fid)