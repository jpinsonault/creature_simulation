import sys
sys.path.insert(0, '../../')
from NeuralNetworks.MultiNN_c import MultiNN_c
from NeuralNetworks.MultiNN import MultiNN
from time import time

num_networks = 10000
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
nnc.initialize_random_networks(10)
nnc.compute_all_networks()

end_time = time()

###############################################
cython_time = end_time - start_time
print("Cython Execution time: {}s".format(cython_time))
print("Improvement: {}%".format((python_time/cython_time-1)*100))

print(nn.get_networks().shape)