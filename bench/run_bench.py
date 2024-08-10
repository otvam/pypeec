import os
import time
import joblib
import multiprocessing
import mod_solver
from pypeec import log
from pypeec import io

# create the logger
LOGGER = log.get_logger(__name__, "bench")

(data_voxel, data_problem) = io.load_data("out.pck")
data_tolerance = io.load_input("tolerance.yaml")

n_par = int(os.getenv("PARALLEL"))
n_des = n_par*8

idx = range(n_des)
data_voxel = [data_voxel] * len(idx)
data_problem = [data_problem] * len(idx)
data_tolerance = [data_tolerance] * len(idx)

###########################################################################################
###########################################################################################

now_1 = time.time()
LOGGER.info("======== start")
joblib.Parallel(n_jobs=n_par, backend="loky")(
    joblib.delayed(mod_solver.fct_compute)(*arg) for arg in zip(idx, data_voxel, data_problem, data_tolerance)
)
LOGGER.info("======== end")
now_2 = time.time()
LOGGER.info("======== time = %f" % (now_2 - now_1))

###########################################################################################
###########################################################################################

now_1 = time.time()
LOGGER.info("======== start")
pool = multiprocessing.Pool(n_par)
pool.starmap(mod_solver.fct_compute, zip(idx, data_voxel, data_problem, data_tolerance))
pool.close()
LOGGER.info("======== end")
now_2 = time.time()
LOGGER.info("======== time = %f" % (now_2 - now_1))

from joblib import Parallel, delayed, parallel_config
parallel_config
###########################################################################################
###########################################################################################
