# Compile command: python setup.py build_ext --inplace --compiler=mingw32

import numpy as np
cimport numpy as np
from math import tanh

NP_FLOAT = np.float
ctypedef np.float_t NP_FLOAT_t


cdef class MultiNN_c:
    '''
    A cython version of NeuralNetorks.py
    MultiNN holds a collection of Neural Networks' weights and biases.
    All the NNs have to have the same shape
    '''

    cdef int num_networks
    cdef int num_inputs
    cdef int num_hidden
    cdef int num_outputs
    cdef int num_weights
    cdef np.ndarray networks
    cdef np.ndarray inputs
    cdef np.ndarray outputs
    cdef np.ndarray hidden_sums
    cdef np.ndarray hidden_outputs

    def __init__(self, num_networks, num_inputs, num_hidden, num_outputs):
        self.num_networks = num_networks
        self.num_inputs = num_inputs
        self.num_hidden = num_hidden
        self.num_outputs = num_outputs
        self.num_weights = (num_inputs * num_hidden) + (num_hidden * num_outputs) + num_hidden + num_outputs
        self.networks = np.zeros((num_networks, self.num_weights), dtype=NP_FLOAT)
        self.inputs = np.zeros((num_networks, num_inputs), dtype=NP_FLOAT)
        self.outputs = np.zeros((num_networks, num_outputs), dtype=NP_FLOAT)

        # Buffers for calculations
        self.hidden_sums = np.zeros((num_hidden), dtype=NP_FLOAT)
        self.hidden_outputs = np.zeros((num_hidden), dtype=NP_FLOAT)

    def initialize_random_networks(self, float limit):
        self.networks = np.random.rand(self.num_networks, self.num_weights)
        self.networks = (self.networks - .5) * (limit * 2)

    def set_inputs(self, nn_index, inputs):
        if inputs.shape != (self.num_inputs):
            raise Exception("Shape of inputs doesn't match")

        self.networks[nn_index] = inputs

    def set_all_inputs(self, inputs):
        if inputs.shape != (self.num_networks, self.num_inputs):
            raise Exception("Shape of inputs doesn't match")

        self.networks = inputs

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

        cdef int index
        for index in range(self.num_networks):
            self.compute_network(index)

    def compute_network(self, int nn_index):
        cdef np.ndarray weights = self.networks[nn_index]
        cdef np.ndarray inputs = self.inputs[nn_index]
        cdef np.ndarray outputs = self.outputs[nn_index]

        cdef int weights_index = 0

        cdef int hidden_index
        cdef int input_index
        cdef int output_index

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

    def hyperTan(self, float x):
        if x < -20.0:
            return -1.0
        elif x > 20.0:
            return 1.0
        else:
            return tanh(x)
