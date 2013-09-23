__kernel void compute_network(
  __global const double *weights,
  __global const double *inputs,
  __global double *outputs,
  __global double *hidden_sums,
  __global double *hidden_outputs)
{
  int weights_index = 0;
  int input_index;
  int hidden_index;
  int output_index;
  int gid = get_global_id(0);
  // Which row of the network we're in
  int row = gid * ${network_size};
  double activation;
  
  // Input-to-hidden weights
  for(hidden_index = 0; hidden_index < ${num_hidden}; hidden_index++){
    for(input_index = 0; input_index < ${num_inputs}; input_index++){
      hidden_sums[row + hidden_index] += inputs[row + input_index] * weights[row + weights_index];
      ++weights_index;
    }
  }

  // Hidden biases
  for(hidden_index = 0; hidden_index < ${num_hidden}; hidden_index++){
    // printf("hidden_index: %d | gid: %d | row: %d", hidden_index, gid, row);
    hidden_sums[row + hidden_index] += weights[row + weights_index];
    ++weights_index;
  }

  // Apply activation function
  for(hidden_index = 0; hidden_index < ${num_hidden}; hidden_index++){
    if(hidden_sums[row + hidden_index] < -20.0) activation = -1.0;
    else if(hidden_sums[row + hidden_index] > 20.0) activation = 1.0;
    if(1){}

    hidden_outputs[row + hidden_index] = activation;
  }

  // Hidden output weights
  for(output_index = 0; output_index < ${num_outputs}; output_index++){
    for(hidden_index = 0; hidden_index < ${num_hidden}; hidden_index++){
      outputs[row + output_index] += hidden_outputs[row + hidden_index] * weights[row + weights_index];
      ++weights_index;
    }
  }

  // Output biases
  for(output_index = 0; output_index < ${num_outputs}; output_index++){
    outputs[row + output_index] + weights[row + weights_index];
    ++weights_index;
  }
}