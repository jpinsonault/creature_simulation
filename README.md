neural_networks
===============

Messing around with neural networks and genetic algorithms

To build the cython modules in game_files and NeuralNetworks, run this in both directories

`python setup.py build_ext --inplace`

or if you're on windows and using mingw:

`python setup.py build_ext --inplace --compiler=mingw32`

When developing, you can just run `python run-compile.py`, which will compile and then run creature_sim.py

