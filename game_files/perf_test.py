from operator import add
import operator
from itertools import izip
import time
from pprint import pprint

def direct_add_2(first, second):
    first[0] += second[0]
    first[1] += second[1]


def while_add_length_not_given(first, second):
    index = 0
    length = len(first)

    while index < length:
        first[index] += second[index]
        index += 1


def while_add_length_given(first, second):
    index = 0
    length = 2
    while index < length:
        first[index] += second[index]
        index += 1


def for_xrange_add(first, second):
    for index in xrange(2):
        first[index] += second[index]


def for_range_add(first, second):
    for index in range(2):
        first[index] += second[index]


def zip_add(first_list, second_list):
    first_list[:] = [first + second for first, second in zip(first_list, second_list)]


def izip_add(first_list, second_list):
    first_list[:] = [first + second for first, second in izip(first_list, second_list)]


def map_add(first, second):
    first[:] = map(add, first, second)


add_functions = {
    "direct_add_2": direct_add_2,
    "while_add_length_not_given": while_add_length_not_given,
    "while_add_length_given": while_add_length_given,
    "zip_add": zip_add,
    "izip_add": izip_add,
    "map_add": map_add,
    "for_range_add": for_range_add,
    "for_xrange_add": for_xrange_add,
}

NUM_ITERATIONS = 1000000
RUNS_TO_AVERAGE = 1

def main():
    timings = dict([[name, 0] for name in add_functions.keys()])

    for run_number in range(RUNS_TO_AVERAGE):
        for name, function in add_functions.items():
            time_start = time.time()

            point = [1, 2]
            point2 = [10, 10]
            for x in xrange(NUM_ITERATIONS):
                function(point, point2)

            time_end = time.time()
            timings[name] += (time_end - time_start)




    for name, timing in timings.items():
        timings[name] /= RUNS_TO_AVERAGE

    sorted_timings = sorted(timings.iteritems(), key=operator.itemgetter(1))

    print("Average of {} runs:".format(RUNS_TO_AVERAGE))
    print("{} iterations of each function".format(NUM_ITERATIONS))
    for timing in sorted_timings:
        print("{}: {:0.3f} seconds".format(timing[0], timing[1]))


def unit_test():
    correct_result = [1, 2]
    direct_add_2(correct_result, [10, 10])

    for name, function in add_functions.items():
        point = [1, 2]
        point2 = [10, 10]
        
        function(point, point2)

        assert(point == correct_result)

    print("Test passed")


if __name__ == '__main__':
    main()
    # unit_test()

