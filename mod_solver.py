from pypeec import main
from pypeec import log

# create the logger
LOGGER = log.get_logger(__name__, "bench")


def fct_compute(idx, data_voxel, data_problem, data_tolerance):
    LOGGER.info("    idx = %d" % idx)

    main.run_solver_data(data_voxel, data_problem, data_tolerance)
