import data_trf
from solver import problem_geometry
from solver import green_function
from solver import voxel_geometry
from solver import resistance_inductance
from solver import equation_system
from solver import equation_solver
from solver import extract_solution
from solver import check_data
import numpy as np

data_solver = data_trf.get_data_solver()

######################################################## CHECK

assert isinstance(data_solver, dict), "invalid input data"
(n, d, n_green_simplify) = check_data.check_voxel(data_solver)
(freq, solver_options) = check_data.check_solver(data_solver)
(conductor, src_current, src_voltage) = check_data.check_problem(data_solver)

######################################################## INIT



xyz = voxel_geometry.get_voxel_coordinate(d, n)

A_incidence = voxel_geometry.get_incidence_matrix(n)

######################################################## GREEN

(G_mutual, G_self) = green_function.get_green_tensor(d, n, n_green_simplify)

######################################################## PARSE

(idx_v, rho_v) = problem_geometry.get_conductor_geometry(conductor)
(idx_src_c, val_src_c, idx_src_v, val_src_v) = problem_geometry.get_source_geometry(src_current, src_voltage)

(A_reduced, idx_f_x, idx_f_y, idx_f_z, idx_f) = problem_geometry.get_incidence_matrix(n, A_incidence, idx_v)
(idx_src_c_local, idx_src_v_local) = problem_geometry.get_source_index(n, idx_v, idx_src_c, idx_src_v)

problem_status = problem_geometry.get_status(n, idx_v, idx_f, idx_src_c, idx_src_v)

######################################################## MATRIX

(R_tensor, R_vector) = resistance_inductance.get_resistance_matrix(n, d, idx_v, rho_v, idx_f_x, idx_f_y, idx_f_z, idx_f)

(L_tensor, L_vector) = resistance_inductance.get_inductance_matrix(n, d, idx_f, G_mutual, G_self)

(ZL_tensor, ZL_vector) = resistance_inductance.get_inductance_operator(n, freq, L_tensor, L_vector)

######################################################## EQN

rhs = equation_system.get_source_vector(idx_v, idx_f, idx_src_c_local, val_src_c, val_src_v)
(A_kcl, A_kvl, A_src) = equation_system.get_connection_matrix(A_reduced, idx_v, idx_f, idx_src_v_local)

pcd_op = equation_system.get_preconditioner_operator(idx_v, idx_f, idx_src_v_local, A_kcl, A_kvl, A_src, R_vector, ZL_vector)
sys_op = equation_system.get_system_operator(n, idx_v, idx_f, idx_src_v_local, A_kcl, A_kvl, A_src, R_tensor, ZL_tensor)

S_matrix = equation_system.get_singular(A_kcl, A_kvl, A_src)

######################################################## SOLVE

cond = equation_solver.get_condition(S_matrix)
(sol, solver_status) = equation_solver.get_solver(sys_op, pcd_op, rhs, cond, solver_options)

######################################################## EXTRACT

(I_face, V_voxel, I_src_v) = extract_solution.get_sol_extract(n, idx_f, idx_v, idx_src_v, sol)

J_voxel = extract_solution.get_current_density(n, d, A_incidence, I_face)

src_terminal = extract_solution.get_src_terminal(src_current, src_voltage, V_voxel, I_src_v)

# A_incidence = A_incidence.toarray()
# mdic = {"xyz": xyz, "A_incidence": A_incidence, "G_mutual": G_mutual, "G_self": G_self}
# scipy.io.savemat("matlab_matrix.mat", mdic)

# mdic = {"L_tensor": L_tensor, "L_vector": L_vector, "R_tensor": R_tensor, "R_vector": R_vector}
# scipy.io.savemat("matlab_matrix.mat", mdic)

print(problem_status)
print(solver_status)

print('ok')
