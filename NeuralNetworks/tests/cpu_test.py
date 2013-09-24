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

nncl = MultiNN(num_networks, num_input, num_hidden, num_output)
nncl.initialize_random_networks(10)
nncl.setup_opencl()
nncl.run_cpu_test()

end_time = time()

python_time = end_time - start_time
print("Python Execution time: {}s".format(python_time))

