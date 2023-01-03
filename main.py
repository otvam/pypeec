import data_trf
from main import solver

data_solver = data_trf.get_data_solver()

data_res = solver.run(data_solver)

print('ok')
