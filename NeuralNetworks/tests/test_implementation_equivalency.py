import sys
# Path to import NeuralNetworks
sys.path.insert(0, '../../')
import unittest
import numpy as np

from NeuralNetworks.MultiNN import MultiNN
from NeuralNetworks.MultiNN_c import MultiNN_c
 
class ImplementationEquivalencyTests(unittest.TestCase):

   def setUp(self):
      self.num_networks = 100
      self.num_inputs = 3
      self.num_hidden = 7
      self.num_outputs = 2
      self.random_limit = 10
      # decimal places to round
      self.round = 5
   
   def test_multiNN_python_output_same_as_cpython(self):
      python_nn = MultiNN(self.num_networks, self.num_inputs, self.num_hidden, self.num_outputs)
      cython_nn = MultiNN_c(self.num_networks, self.num_inputs, self.num_hidden, self.num_outputs)

      python_nn.initialize_random_networks(self.random_limit)
      cython_nn.set_networks(python_nn.networks[:])

      python_nn.compute_all_networks()
      cython_nn.compute_all_networks()

      # We round the arrays because cython and python sometimes differ on the last decimal place
      self.assertTrue(np.array_equal(np.around(cython_nn.get_networks(), self.round), np.around(python_nn.get_networks(), self.round)))


if __name__ == '__main__':
    unittest.main()