__kernel void compute_network(
  __global double *weights,
  __global double *inputs,
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
  int w_row = gid * ${network_size};
  int i_row = gid * ${num_inputs};
  int h_row = gid * ${num_hidden};
  int o_row = gid * ${num_outputs};
  double activation;

  // Input-to-hidden weights
  for(hidden_index = 0; hidden_index < ${num_hidden}; hidden_index++){
    for(input_index = 0; input_index < ${num_inputs}; input_index++){
      hidden_sums[h_row + hidden_index] += inputs[i_row + input_index] * weights[w_row + weights_index];

      ++weights_index;
    }
  }
  // for (int i = 0; i < ${num_hidden}; i++){
  //   printf("%f\n", hidden_sums[h_row + i]);
  // }
  // printf("Done with Input-to-hidden weights\n");

  // Hidden biases
  for(hidden_index = 0; hidden_index < ${num_hidden}; hidden_index++){
    hidden_sums[h_row + hidden_index] += weights[w_row + weights_index];
    ++weights_index;
  }
  // printf("Done with Hidden biases\n");


  // Apply activation function
  for(hidden_index = 0; hidden_index < ${num_hidden}; hidden_index++){
    if(hidden_sums[h_row + hidden_index] < -20.0) activation = -1.0;
    else if(hidden_sums[h_row + hidden_index] > 20.0) activation = 1.0;
    
    hidden_outputs[o_row + hidden_index] = activation;
  }

  // printf("Done with Apply activation function\n");


  // Hidden output weights
  for(output_index = 0; output_index < ${num_outputs}; output_index++){
    for(hidden_index = 0; hidden_index < ${num_hidden}; hidden_index++){
      outputs[o_row + output_index] += hidden_outputs[o_row + hidden_index] * weights[w_row + weights_index];
      ++weights_index;
    }
  }

  // printf("Done with Hidden output weights\n");


  // Output biases
  for(output_index = 0; output_index < ${num_outputs}; output_index++){
    outputs[o_row + output_index] += weights[w_row + weights_index];
    // printf("%f\n", outputs[o_row + output_index]);
    ++weights_index;
  }

  // printf("Done\n");

}