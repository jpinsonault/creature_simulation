import numpy
import pyopencl as cl
import os
from os.path import dirname
from os.path import join
from math import tanh
from mako.template import Template


class MultiNN:
    '''
    MultiNN holds a collection of Neural Networks' weights and biases.
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
        self.hidden_sums = numpy.ones((num_networks, num_hidden))
        # self.hidden_sums = numpy.zeros((num_networks, num_hidden))
        self.hidden_outputs = numpy.zeros((num_networks, num_hidden))

    def initialize_random_networks(self, limit):
        self.networks = numpy.random.rand(self.num_networks, self.num_weights)
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

        for index in range(self.num_networks):
            self.compute_network(index)

    def compute_network(self, nn_index):
        weights = self.networks[nn_index]
        inputs = self.inputs[nn_index]
        outputs = self.outputs[nn_index]

        hidden_sums = self.hidden_sums[nn_index]
        hidden_outputs = self.hidden_outputs[nn_index]

        weights_index = 0

        # Input-to-hidden weights
        for hidden_index in range(self.num_hidden):
            for input_index in range(self.num_inputs):
                hidden_sums[hidden_index] += inputs[input_index] * weights[weights_index]
                weights_index += 1

        # print(hidden_sums)

        # Hidden biases
        for hidden_index in range(self.num_hidden):
            hidden_sums[hidden_index] += weights[weights_index]
            weights_index += 1

        # Apply activation function
        for hidden_index in range(self.num_hidden):
            hidden_outputs[hidden_index] = self.hyperTan(hidden_sums[hidden_index])

        # Hidden output weights
        for output_index in range(self.num_outputs):
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

    def setup_opencl(self):
        """

        """
        # Size in bytes
        float_size = 8
        hidden_buffer_size = float_size * self.num_networks * self.num_hidden

        # Some arrays for intermediate values in the calculations
        self.cl_hidden_sums = numpy.zeros((self.num_networks, self.num_hidden))
        self.cl_hidden_outputs = numpy.zeros((self.num_networks, self.num_hidden))

        # Setup context, queue
        # Set to use GPU
        platform = cl.get_platforms()
        my_gpu_devices = platform[0].get_devices(device_type=cl.device_type.CPU)
        for device in my_gpu_devices:
            print(device)

        self.cl_context = cl.Context(devices=my_gpu_devices)
        self.cl_queue = cl.CommandQueue(self.cl_context)

        # Setup buffers
        mf = cl.mem_flags

        self.cl_networks_buf = cl.Buffer(self.cl_context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=self.networks)
        self.cl_inputs_buf = cl.Buffer(self.cl_context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=self.inputs)
        self.cl_outputs_buf = cl.Buffer(self.cl_context, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=self.outputs)

        self.cl_hidden_sums_buf = cl.Buffer(self.cl_context, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=self.hidden_sums)
        self.cl_hidden_outputs_buf = cl.Buffer(self.cl_context, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=self.hidden_outputs)

        # Get kernel, send parameters for the mako file
        self.kernel_compute_network = self.get_kernel("kernel_compute_network", network_size=self.num_weights, num_hidden=self.num_hidden, num_inputs=self.num_inputs, num_outputs=self.num_outputs, num_networks=self.num_networks)

        self.cl_program = cl.Program(self.cl_context, self.kernel_compute_network).build()
        print(self.kernel_compute_network)

    def compute_all_networks_opencl(self):
        compute_network_event = self.cl_program.compute_network(self.cl_queue, (self.num_networks, ), None, self.cl_networks_buf, self.cl_inputs_buf, self.cl_outputs_buf, self.cl_hidden_sums_buf, self.cl_hidden_outputs_buf)

        compute_network_event.wait()
        cl.enqueue_read_buffer(self.cl_queue, self.cl_outputs_buf, self.outputs).wait()

    def run_cpu_test(self):
        test_kernel = self.get_kernel("kernel_cpu_test")

        test_program = cl.Program(self.cl_context, test_kernel).build()

        event = test_program.test(self.cl_queue, (self.num_networks,), None)
        event.wait()

    def get_kernel(self, file_name, **parameters):
        # get current directory, look in kernels/ for the mako file
        path = join(dirname(__file__), 'kernels/{}.mako'.format(file_name))
        with open(path, 'r') as kernel_file:
            text = kernel_file.read()
            return Template(text).render(**parameters)
