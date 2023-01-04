import data_trf
from plotter import manage_voxel
import pickle

with open('data_trf.pck', 'rb') as fid:
    data_res = pickle.load(fid)


n = data_res["n"]
d = data_res["d"]
idx_v = data_res["idx_v"]

manage_voxel.plot_geom(data_res)