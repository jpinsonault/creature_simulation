import sys
sys.path.insert(0, '../../')
from NeuralNetworks.MultiNN_c import MultiNN_c
from NeuralNetworks.MultiNN import MultiNN
from time import time

num_networks = 400
num_input = 3
num_hidden = 7
num_output = 2

###############################################
start_time = time()

nn = MultiNN(num_networks, num_input, num_hidden, num_output)
nn.initialize_random_networks(10)

nn.compute_all_networks()

end_time = time()

python_time = end_time - start_time

###############################################
nn.initialize_random_networks(10)
start_time = time()

nnc = MultiNN_c(num_networks, num_input, num_hidden, num_output)
nnc.compute_all_networks()

end_time = time()
cython_time = end_time - start_time

###############################################

# nncl = MultiNN(num_networks, num_input, num_hidden, num_output)
# nncl.set_networks(nn.get_networks())

# nncl.setup_opencl()
start_time = time()

# nncl.compute_all_networks_opencl()

end_time = time()

opencl_time = end_time - start_time

###############################################
print("Python Execution time: {:.2f}s".format(python_time))
print("Cython Execution time: {:.2f}s".format(cython_time))
print("opencl Execution time: {:.2f}s".format(opencl_time))

print("Improvement from python to cython: {:.2f}x faster".format((python_time/cython_time)))
# print("Improvement from python to opencl: {:.2f}x faster".format((python_time/opencl_time)))
# print("Improvement from cython to opencl: {:.2f}x faster".format((cython_time/opencl_time)))