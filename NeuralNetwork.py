from random import uniform
from math import tanh

WEIGHT_LIMIT = 2.0

def _random_weight():
    return uniform(-WEIGHT_LIMIT, WEIGHT_LIMIT)

class NeuralNetwork(object):
    '''
        Holds a NeuralNetwork
    '''

    def __init__(self, num_inputs, num_hidden, num_outputs):
        super(NeuralNetwork, self).__init__()
        self.num_inputs = num_inputs
        self.num_hidden = num_hidden
        self.num_outputs = num_outputs
        self.num_weights = (num_inputs * num_hidden) + (num_hidden * num_outputs) + num_hidden + num_outputs
        self.weights = [0 for x in range(self.num_weights)]
        # self.weights = numpy.zeros((num_networks, self.num_weights))
        self.inputs = [0 for x in range(num_inputs)]
        # self.inputs = numpy.zeros((num_networks, num_inputs))
        self.outputs = [0 for x in range(num_outputs)]
        # self.outputs = numpy.zeros((num_networks, num_outputs))

        # Buffers for calculations
        # self.hidden_sums = numpy.zeros((num_networks, num_hidden))
        self.hidden_sums = [0 for x in range(num_hidden)]
        # self.hidden_sums = numpy.zeros((num_networks, num_hidden))
        # self.hidden_outputs = numpy.zeros((num_networks, num_hidden))
        self.hidden_outputs = [0 for x in range(num_hidden)]

    def initialize_random_network(self):
        # self.weights = numpy.random.rand(self.num_networks, self.num_weights)
        self.weights = [_random_weight() for x in range(self.num_weights)]
        # self.weights = (self.weights - .5) * (limit * 2)

    def set_inputs(self, inputs):
        self.inputs = inputs

    def get_network(self):
        return self.weights

    def set_network(self, weights):
        if len(weights) != self.num_weights:
            raise Exception("Number of weights doesn't match")

        self.weights = weights

    def get_inputs(self):
        return self.inputs

    def get_outputs(self):
        return self.outputs

    def print_network(self):
        print(self.weights)

    def compute_network(self):
        weights = self.weights
        inputs = self.inputs
        outputs = self.outputs

        hidden_sums = self.hidden_sums
        hidden_outputs = self.hidden_outputs

        weights_index = 0

        # Input-to-hidden weights
        for hidden_index in range(self.num_hidden):
            hidden_sums[hidden_index] = 0.0
            for input_index in range(self.num_inputs):
                hidden_sums[hidden_index] += inputs[input_index] * weights[weights_index]
                weights_index += 1

        # Hidden biases
        for hidden_index in range(self.num_hidden):
            hidden_sums[hidden_index] += weights[weights_index]
            weights_index += 1

        # Apply activation function
        for hidden_index in range(self.num_hidden):
            hidden_outputs[hidden_index] = self.hyperTan(hidden_sums[hidden_index])

        # Hidden output weights
        for output_index in range(self.num_outputs):
            outputs[output_index] = 0.0
            for hidden_index in range(self.num_hidden):
                outputs[output_index] += hidden_outputs[hidden_index] * weights[weights_index]
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
