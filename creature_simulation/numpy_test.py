from numpy_cython import *
from timeit import timeit

def py_array_assignment():
    py_array = [1, 2]
    for x in xrange(NUM_ITERATIONS):
        py_array[0] += 1
        py_array[1] += 1


def main():
    print(timeit(py_array_assignment, number=3))
    print(timeit(np_array_assignment, number=3))

if __name__ == '__main__':
    main()