set -e

python setup.py build_ext --inplace

python creature_simulation.py