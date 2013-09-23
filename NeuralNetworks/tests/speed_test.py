import sys
sys.path.insert(0, '../../')
from NeuralNetworks.MultiNN_c import MultiNN_c
from NeuralNetworks.MultiNN import MultiNN
from time import time

num_networks = 40
num_input = 3
num_hidden = 7
num_output = 2
###############################################

start_time = time()

nn = MultiNN(num_networks, num_input, num_hidden, num_output)
nn.compute_all_networks()
nn.initialize_random_networks(10)

end_time = time()

python_time = end_time - start_time
print("Python Execution time: {}s".format(python_time))

###############################################
start_time = time()

nnc = MultiNN_c(num_networks, num_input, num_hidden, num_output)
nnc.set_networks(nn.get_networks())
nnc.compute_all_networks()

end_time = time()
cython_time = end_time - start_time
print("Cython Execution time: {}s".format(cython_time))

###############################################

nncl = MultiNN(num_networks, num_input, num_hidden, num_output)
nncl.set_networks(nn.get_networks())

nncl.setup_opencl()
start_time = time()

# print(nncl.kernel_compute_network)
nncl.compute_all_networks_opencl()

end_time = time()
opencl_time = end_time - start_time
print("opencl Execution time: {}s".format(opencl_time))

###############################################
print("Improvement from python to cython: {}%".format((python_time/cython_time-1)*100))
print("Improvement from python to opencl: {}%".format((python_time/opencl_time-1)*100))
print("Improvement from cython to opencl: {}%".format((cython_time/opencl_time-1)*100))