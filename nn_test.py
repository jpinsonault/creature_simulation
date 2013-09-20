from NeuralNetworks import MultiNN
import datetime
from time import time

start_time = time()
nn = MultiNN(30000, 3, 5, 2)

nn.initialize_random_networks(10)
# nn.print_networks()
# print(nn.outputs.shape)
nn.compute_all_networks()

end_time = time()
print("Execution time: ", end_time - start_time, "s")

# print(nn.outputs)
