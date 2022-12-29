import data_trf
from method_init import init_matrix
from method_init import green_function
from method_solve import solve_matrix
import scipy.io

data_init = data_trf.get_data_init()
data_solve = data_trf.get_data_solve()

nx = data_init["nx"]
ny = data_init["ny"]
nz = data_init["nz"]
dx = data_init["dx"]
dy = data_init["dy"]
dz = data_init["dz"]
n_min_center = data_init["n_min_center"]

conductor = data_solve["conductor"]
src_current = data_solve["src_current"]
src_voltage = data_solve["src_voltage"]

n = (nx, ny, nz)
d = (dx, dy, dz)

xyz = init_matrix.get_voxel_coordinate(d, n)

A_incidence = init_matrix.get_incidence_matrix(n)

(G_mutual, G_self) = green_function.get_green_tensor(d, n, n_min_center)


(idx_c, rho_c) = solve_matrix.get_conductor_geometry(conductor)
(idx_src_c, val_src_c, idx_src_v, val_src_v) = solve_matrix.get_source_geomtry(src_current, src_voltage)

# A_incidence = A_incidence.toarray()
# mdic = {"xyz": xyz, "A_incidence": A_incidence, "G_mutual": G_mutual, "G_self": G_self}
# scipy.io.savemat("matlab_matrix.mat", mdic)

print('ok')