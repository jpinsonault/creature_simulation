from random import uniform
# from math import tanh
import numpy as np
cimport numpy as np
cimport cython
from libc.math cimport tanh
cdef extern from "math.h":
    double tanh(double x)

DTYPE = np.int
ctypedef np.float_t NP_FLOAT

cdef class NeuralNetwork:
    '''
        Holds a NeuralNetwork
    '''

    cdef int num_inputs
    cdef int num_hidden
    cdef int num_outputs
    cdef int num_weights
    cdef np.ndarray weights
    cdef np.ndarray inputs
    cdef np.ndarray outputs
    cdef np.ndarray hidden_sums
    cdef np.ndarray hidden_outputs

    def __init__(self, int num_inputs, int num_hidden, int num_outputs):
        self.num_inputs = num_inputs
        self.num_hidden = num_hidden
        self.num_outputs = num_outputs
        self.num_weights = (num_inputs * num_hidden) + (num_hidden * num_outputs) + num_hidden + num_outputs
        # self.weights = [0 for x in xrange(self.num_weights)]
        self.weights = np.zeros(self.num_weights)
        # self.inputs = [0 for x in xrange(num_inputs)]
        self.inputs = np.zeros(num_inputs)
        # self.outputs = [0 for x in xrange(num_outputs)]
        self.outputs = np.zeros(num_outputs)

        # Buffers for calculations
        self.hidden_sums = np.zeros(num_hidden)
        # self.hidden_sums = [0 for x in xrange(num_hidden)]
        # self.hidden_sums = np.zeros((num_networks, num_hidden))
        self.hidden_outputs = np.zeros(num_hidden)
        # self.hidden_outputs = [0 for x in xrange(num_hidden)]

    def initialize_random_network(self, limit):
        self.weights = np.random.rand(self.num_weights)
        self.weights = (self.weights - .5) * (limit * 2)
        # self.weights = [uniform(-limit, limit) for x in xrange(self.num_weights)]
        
    def set_inputs(self, inputs):
        self.weights = np.array(inputs)

    def get_networks(self):
        return self.weights

    def set_networks(self, weights):
        self.weights = weights

    def get_outputs(self):
        cdef float out1 = self.outputs[0]
        cdef float out2 = self.outputs[1]
         
        return (out1, out2)

    def print_network(self):
        print(self.weights)

    @cython.boundscheck(False)
    def compute_network(self):
        cdef np.ndarray[NP_FLOAT, ndim=1] weights = self.weights
        cdef np.ndarray[NP_FLOAT, ndim=1] inputs = self.inputs
        cdef np.ndarray[NP_FLOAT, ndim=1] outputs = self.outputs

        cdef np.ndarray[NP_FLOAT, ndim=1] hidden_sums = self.hidden_sums
        cdef np.ndarray[NP_FLOAT, ndim=1] hidden_outputs = self.hidden_outputs

        cdef int weights_index = 0

        cdef int num_hidden = self.num_hidden
        cdef int num_outputs = self.num_outputs

        cdef int index = 0
        for index in range(num_hidden):
            hidden_outputs[index] = 0.0

        for index in range(num_outputs):
            outputs[index] = 0.0

        # Input-to-hidden weights
        for hidden_index in range(num_hidden):
            for input_index in range(self.num_inputs):
                hidden_sums[hidden_index] += inputs[input_index] * weights[weights_index]
                weights_index += 1

        # Hidden biases
        for hidden_index in range(num_hidden):
            hidden_sums[hidden_index] += weights[weights_index]
            weights_index += 1

        # Apply activation function
        for hidden_index in range(num_hidden):
            hidden_outputs[hidden_index] = self.hyperTan(hidden_sums[hidden_index])

        # Hidden output weights
        for output_index in range(num_outputs):
            for hidden_index in range(num_hidden):
                outputs[output_index] += hidden_outputs[hidden_index] * weights[weights_index]
                weights_index += 1

        # Output biases
        for output_index in range(num_outputs):
            outputs[output_index] += weights[weights_index]
            weights_index += 1


    cdef float hyperTan(self, float x):
        if x < -20.0:
            return -1.0
        elif x > 20.0:
            return 1.0
        else:
            return tanh(x)
