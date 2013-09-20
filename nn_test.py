from NeuralNetworks import MultiNN


nn = MultiNN(5, 2, 4, 1)

nn.initialize_random_networks(10)
# nn.print_networks()
print(nn.outputs.shape)
nn.compute_all_networks()

print(nn.outputs)
