from plotter import manage_voxel
from plotter import manage_plot
import pickle
import pyvista as pv

with open('data_trf.pck', 'rb') as fid:
    (status, data_res) = pickle.load(fid)


n = data_res["n"]
d = data_res["d"]
ori = data_res["ori"]
idx_voxel = data_res["idx_voxel"]
rho_voxel = data_res["rho_voxel"]
V_voxel = data_res["V_voxel"]
J_voxel = data_res["J_voxel"]
src_terminal = data_res["src_terminal"]

plot_options = {
    "grid_plot": True,
    "grid_thickness": 1.0,
    "grid_opacity": 0.2,
    "geom_plot": True,
    "geom_thickness": 1.0,
    "geom_opacity": 0.2,
}

(grid, geom) = manage_voxel.get_geom(n, d, ori, idx_voxel)
geom = manage_voxel.get_material(idx_voxel, geom, src_terminal)
geom = manage_voxel.get_resistivity(idx_voxel, geom, rho_voxel)
geom = manage_voxel.get_potential(idx_voxel, geom, V_voxel)
geom = manage_voxel.get_current_density(idx_voxel, geom, J_voxel)

data_options = {
    "legend": "Material Type",
    "title": "Material",
}

# pl = pv.Plotter()
# manage_plot.plot_geom(pl, grid, geom, plot_options, data_options)
# pl.show(title="ra")

data_options = {
    "data": "rho",
    "scale": 1e8,
    "log": False,
    "range": [-float("inf"), +float("inf")],
    "legend": "Resistivity [uOhm/cm]",
    "title": "Resistivity",
}

# pl = pv.Plotter()
# manage_plot.plot_scalar(pl, grid, geom, plot_options, data_options)
# pl.show(title="ra")

data_options = {
    "data_norm": "J_norm_re",
    "data_vec": "J_vec_re",
    "scale": 1e-6,
    "arrow": 1e-6,
    "log": False,
    "range": [50, 90],
    "legend": "Current Density [A/mm2]",
    "title": "Current Density",
}

pl = pv.Plotter()
manage_plot.plot_arrow(pl, grid, geom, plot_options, data_options)
pl.show(title="ra")
