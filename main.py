import data_trf
from solver import problem_geometry
from solver import green_function
from solver import voxel_geometry
from solver import resistance_inductance
from solver import equation_system
from solver import equation_solver

data_init = data_trf.get_data_init()
data_solve = data_trf.get_data_solve()

nx = data_init["nx"]
ny = data_init["ny"]
nz = data_init["nz"]
dx = data_init["dx"]
dy = data_init["dy"]
dz = data_init["dz"]
n_min_center = data_init["n_min_center"]

freq = data_solve["freq"]
solver_options = data_solve["solver_options"]
conductor = data_solve["conductor"]
src_current = data_solve["src_current"]
src_voltage = data_solve["src_voltage"]

n = (nx, ny, nz)
d = (dx, dy, dz)

######################################################## INIT

xyz = voxel_geometry.get_voxel_coordinate(d, n)

A_incidence = voxel_geometry.get_incidence_matrix(n)

(G_mutual, G_self) = green_function.get_green_tensor(d, n, n_min_center)

######################################################## PARSE

(idx_v, rho_v) = problem_geometry.get_conductor_geometry(conductor)
(idx_src_c, val_src_c, idx_src_v, val_src_v) = problem_geometry.get_source_geometry(src_current, src_voltage)

(A_reduced, idx_f_x, idx_f_y, idx_f_z, idx_f) = problem_geometry.get_incidence_matrix(n, A_incidence, idx_v)
(idx_src_c_local, idx_src_v_local) = problem_geometry.get_source_index(n, idx_v, idx_src_c, idx_src_v)

######################################################## MATRIX

(R_tensor, R_vector) = resistance_inductance.get_resistance_matrix(n, d, idx_v, rho_v, idx_f_x, idx_f_y, idx_f_z, idx_f)

(L_tensor, L_vector) = resistance_inductance.get_inductance_matrix(n, d, idx_f, G_mutual, G_self)

(ZL_tensor, ZL_vector) = resistance_inductance.get_inductance_operator(n, freq, L_tensor, L_vector)

######################################################## EQN

rhs = equation_system.get_source_vector(idx_v, idx_f, idx_src_c_local, val_src_c, val_src_v)
(A_kcl, A_kvl, A_src) = equation_system.get_connection_matrix(A_reduced, idx_v, idx_f, idx_src_v_local)

pcd_op = equation_system.get_preconditioner_operator(idx_v, idx_f, idx_src_v_local, A_kcl, A_kvl, A_src, R_vector, ZL_vector)
sys_op = equation_system.get_system_operator(n, idx_v, idx_f, idx_src_v_local, A_kcl, A_kvl, A_src, R_tensor, ZL_tensor)

(sol, solver_status) = equation_solver.get_solver(sys_op, pcd_op, rhs, solver_options)


print(sol)
print(solver_status)

# A_incidence = A_incidence.toarray()
# mdic = {"xyz": xyz, "A_incidence": A_incidence, "G_mutual": G_mutual, "G_self": G_self}
# scipy.io.savemat("matlab_matrix.mat", mdic)

# mdic = {"L_tensor": L_tensor, "L_vector": L_vector, "R_tensor": R_tensor, "R_vector": R_vector}
# scipy.io.savemat("matlab_matrix.mat", mdic)

print('ok')
