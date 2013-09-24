__kernel void compute_network(
  __global  double *weights,
  __global  double *inputs,
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

  // for (int i = 0; i < ${network_size}; i++){
  //   if(i < 5){
  //     // printf("gid: %d, i: %d, row: %d, value: %f\n", gid, i, row, weights[row + i]);
  //   }
  // }
  
  // Input-to-hidden weights
  for(hidden_index = 0; hidden_index < ${num_hidden}; hidden_index++){
    for(input_index = 0; input_index < ${num_inputs}; input_index++){
      hidden_sums[row + hidden_index] += inputs[row + input_index] * weights[row + weights_index];
      ++weights_index;
    }
  }
  // printf("Done with Input-to-hidden weights\n");

  // Hidden biases
  for(hidden_index = 0; hidden_index < ${num_hidden}; hidden_index++){
    // printf("hidden_index: %d | gid: %d | row: %d\n", hidden_index, gid, row);
    hidden_sums[row + hidden_index] += weights[row + weights_index];
    ++weights_index;
  }
  // printf("Done with Hidden biases\n");


  // Apply activation function
  for(hidden_index = 0; hidden_index < ${num_hidden}; hidden_index++){
    if(hidden_sums[row + hidden_index] < -20.0) activation = -1.0;
    else if(hidden_sums[row + hidden_index] > 20.0) activation = 1.0;
    
    hidden_outputs[row + hidden_index] = activation;
  }

  // printf("Done with Apply activation function\n");


  // Hidden output weights
  for(output_index = 0; output_index < ${num_outputs}; output_index++){
    for(hidden_index = 0; hidden_index < ${num_hidden}; hidden_index++){
      outputs[row + output_index] += hidden_outputs[row + hidden_index] * weights[row + weights_index];
      ++weights_index;
    }
  }

  // printf("Done with Hidden output weights\n");


  // Output biases
  for(output_index = 0; output_index < ${num_outputs}; output_index++){
    outputs[row + output_index] += weights[row + weights_index];
    // printf("%f\n", outputs[row + output_index]);
    ++weights_index;
  }

  // printf("Done\n");

}