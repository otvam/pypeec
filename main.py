import data_voxel
from method_init import manage_matrix
from method_init import green_function
import scipy.io

data_voxel = data_voxel.get_data()

nx = data_voxel["nx"]
ny = data_voxel["ny"]
nz = data_voxel["nz"]

dx = data_voxel["dx"]
dy = data_voxel["dy"]
dz = data_voxel["dz"]

n_min_center = data_voxel["n_min_center"]

n = (nx, ny, nz)
d = (dx, dy, dz)

xyz = manage_matrix.get_voxel_coordinate(d, n)

A_incidence = manage_matrix.get_incidence_matrix(n)

(G_mutual, G_self) = green_function.get_green_tensor(d, n, n_min_center)


A_incidence = A_incidence.toarray()

mdic = {"xyz": xyz, "A_incidence": A_incidence, "G_mutual": G_mutual, "G_self": G_self}
scipy.io.savemat("matlab_matrix.mat", mdic)
