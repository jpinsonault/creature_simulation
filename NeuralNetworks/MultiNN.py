import numpy
from math import tanh


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
        self.hidden_sums = numpy.zeros((num_hidden))
        self.hidden_outputs = numpy.zeros((num_hidden))

    def initialize_random_networks(self, limit):
        self.networks = numpy.random.rand(self.num_networks, self.num_weights)
        self.networks = (self.networks - .5) * (limit * 2)

    def set_inputs(self, nn_index, inputs):
        if inputs.shape != (self.num_networks, self.num_inputs):
            raise Exception("Shape of inputs doesn't match")

        self.networks[nn_index] = inputs

    def get_networks(self):
        return self.networks

    def set_networks(self, networks):
        self.networks = networks

    def get_outputs(self):
        return self.outputs

    def print_networks(self):
        for network in self.networks:
            print(network)

    def print_network(self, nn_index):
        print(self.networks[nn_index])

    def compute_all_networks(self):
        # for index, network in enumerate(self.networks):
        #     self.compute_network(index)

        for index in range(self.num_networks):
            self.compute_network(index)

    def compute_network(self, nn_index):
        weights = self.networks[nn_index]
        inputs = self.inputs[nn_index]
        outputs = self.outputs[nn_index]

        weights_index = 0

        # Input-to-hidden weights
        for hidden_index in range(self.num_hidden):
            for input_index in range(self.num_inputs):
                self.hidden_sums[hidden_index] += inputs[input_index] * weights[weights_index]
                weights_index += 1

        # Hidden biases
        for hidden_index in range(self.num_hidden):
            self.hidden_sums[hidden_index] += weights[weights_index]
            weights_index += 1

        # Apply activation function
        for hidden_index in range(self.num_hidden):
            self.hidden_outputs[hidden_index] = self.hyperTan(self.hidden_sums[hidden_index])

        # Hidden output weights
        for output_index in range(self.num_outputs):
            for hidden_index in range(self.num_hidden):
                outputs[output_index] += self.hidden_outputs[hidden_index] * weights[weights_index]
                weights_index += 1

        # Output biases
        for output_index in range(self.num_outputs):
            outputs[output_index] += weights[weights_index]
            weights_index += 1

    def hyperTan(self, x):
        if x < -20.0:
            return -1.0
        elif x > 20.0:
            return 1.0
        else:
            return tanh(x)
