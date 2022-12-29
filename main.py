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


(A_reduced, idx_f_x, idx_f_y, idx_f_z, idx_f) = solve_matrix.get_incidence_matrix(n, A_incidence, idx_c)
(R_tensor, R_vector) = solve_matrix.get_resistance_matrix(n, d, idx_c, rho_c, idx_f_x, idx_f_y, idx_f_z, idx_f)

(L_tensor, L_vector) = solve_matrix.get_inductance_matrix(n, d, idx_f, G_mutual, G_self)

A_incidence = A_incidence.toarray()
mdic = {"xyz": xyz, "A_incidence": A_incidence, "G_mutual": G_mutual, "G_self": G_self}
scipy.io.savemat("matlab_matrix.mat", mdic)

# mdic = {"L_tensor": L_tensor, "L_vector": L_vector, "R_tensor": R_tensor, "R_vector": R_vector}
# scipy.io.savemat("matlab_matrix.mat", mdic)

print('ok')