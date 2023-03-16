import time
import numpy as np
from pypeec.lib_matrix import multiply_fft
from pypeec.lib_matrix import multiply_test
from pypeec.lib_matrix import multiply_fft_new

flip = False
matrix_type = "cross"
mat = np.random.rand(3, 3, 3, 3)

# mat = np.random.rand(200, 200, 100, 1)

idx_out = np.array([0, 50, 51, 10])
idx_in = np.array([0, 50, 51, 10])
vec_in = np.array([1, 2, 3, 4])

a = time.time()

data = multiply_fft.get_prepare(idx_out, idx_in, mat, matrix_type)
vec_out = multiply_fft.get_multiply(data, vec_in, matrix_type, flip)
print(vec_out)

data = multiply_fft_new.get_prepare(idx_out, idx_in, mat, matrix_type)
vec_out = multiply_fft_new.get_multiply(data, vec_in, matrix_type, flip)
print(vec_out)

b = time.time()
print(b-a)
