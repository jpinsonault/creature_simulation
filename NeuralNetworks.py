import numpy


class MultiNN:
    '''
    MultiNN holds a collection of Neural Networks' weight and biases.
    All the NNs have to have the same shape
    '''
    def __init__(self, num_networks, num_inputs, num_hidden, num_outputs):
        self.num_networks = num_networks
        self.num_inputs = num_inputs
        self.num_hidden = num_hidden
        self.num_outputs = num_outputs
        self.num_weights = (num_inputs * num_hidden) + (num_hidden * num_outputs) + num_hidden + num_outputs
        self.networks = numpy.zeros((num_networks, self.num_weights))
        self.inputs = numpy.zeros((num_networks, num_inputs))
        self.outputs = numpy.zeros((num_networks, num_outputs))

        # Buffers for calculations
        self.hidden_sums = numpy.zeros((num_networks, num_hidden))
        self.output_sums = numpy.zeros((num_networks, num_outputs))

    def initialize_random_networks(self, limit):
        for index in range(self.num_weights):
            self.networks = numpy.random.rand(self.num_networks, self.num_weights)
            self.networks = (self.networks - .5) * (limit * 2)

    def set_inputs(self, nn_index, inputs):
        if inputs.shape != (self.num_networks, self.num_inputs):
            raise Exception("Shape of inputs doesn't match")

        self.networks[nn_index] = inputs

    def get_outputs(self, nn_index):
        pass

    def print_networks(self):
        for network in self.networks:
            print(network)

    def print_network(self, nn_index):
        print(self.networks[nn_index])

    def compute_all_networks(self):
        for network in self.networks:
            self.compute_network(network)

    def compute_network(self, network):
        for hidden_index in range(self.num_hidden):
            for input_index in range(self.num_inputs):
                # self.hidden_sums[hidden_index] += self.inputs[input_index] * 
                pass