from libc.math cimport abs as abs_c
from libc.math cimport sqrt
from itertools import chain

import numpy as np
cimport numpy as np
from cpython cimport bool


def rotate_around(float cos_radians, float sin_radians, point, pivot, float radians):
    """
        Rotates point around pivot by radians
    """
    cdef float s0_minus_p0
    cdef float s1_minus_p1
    cdef float p0
    cdef float p1

    p0 = pivot[0]
    p1 = pivot[1]
    s0_minus_p0 = point[0] - p0
    s1_minus_p1 = point[1] - p1

    return [cos_radians* s0_minus_p0 - sin_radians* s1_minus_p1 + p0, sin_radians* s0_minus_p0 + cos_radians* s1_minus_p1 + p1]


def rotate_shape(float cos_radians, float sin_radians, shape, pivot, float radians):
    """
        Rotatoes a list of points around pivot by radians
    """
    cdef int length = len(shape)
    cdef index = 0
    rotated_shape = []
    cdef float s0_minus_p0
    cdef float s1_minus_p1
    cdef float p0
    cdef float p1

    for index in range(length):
        p0 = pivot[0]
        p1 = pivot[1]
        s0_minus_p0 = shape[index][0] - p0
        s1_minus_p1 = shape[index][1] - p1
        rotated_shape.append([cos_radians* s0_minus_p0 - sin_radians* s1_minus_p1 + p0, sin_radians* s0_minus_p0 + cos_radians* s1_minus_p1 + p1])

    return rotated_shape



#######################################
# Collision detection functions
#######################################

# utility functions
# _normalize = lambda V: [i / _mag(V) for i in V]         # normalize a vector

cdef _normalize(point, double [2] output):
    cdef double x = point[0]
    cdef double y = point[1]
    cdef double mag = sqrt(x * x + y * y)

    output[0] = x / mag
    output[1] = y / mag

# _intersect = lambda A, B: (A[1] > B[0] and B[1] > A[0]) # intersection test

cdef inline bool _intersect(double [2] first, double [2] second):
    return (first[1] > second[0] and second[1] > first[0])


cdef inline double min_double(double first, double second):
    if first < second:
        return first
    else:
        return second


cdef inline double max_double(double first, double second):
    if first > second:
        return first
    else:
        return second


cdef _project(points, double [2] axis, double[2] output):
    """project self onto axis"""
    # points = self.absolute_shape
    # projected_points = [dot_2d(point, axis) for point in points]

    cdef double x
    cdef double y
    cdef double min_found
    cdef double max_found
    cdef double dot

    for point in points:
        x = point[0]
        y = point[1]

        dot = x * axis[0] + y * axis[1]

        min_found = min_double(min_found, dot)
        max_found = max_double(max_found, dot)

    output[0] = min_found
    output[1] = max_found


class PolygonCython(object):
    """"""
    def collide_bounds(self, second):
        self_bounds = self.get_bounds()
        cdef int a_x = self_bounds[0]
        cdef int a_y = self_bounds[1]
        cdef int a_w = self_bounds[2]
        cdef int a_h = self_bounds[3]

        second_bounds = second.get_bounds()
        cdef int b_x = second_bounds[0]
        cdef int b_y = second_bounds[1]
        cdef int b_w = second_bounds[2]
        cdef int b_h = second_bounds[3]

        a_w = a_w / 2
        a_h = a_h / 2

        a_x = a_x + a_w
        a_y = a_y + a_h

        return ((abs_c(a_x - b_x) < (a_w + b_w)) and
               (abs_c(a_y - b_y) < (a_h + b_h)))

    def collide_poly(self, other):
        """
        test if other polygon collides with self using seperating axis theorem
        if collision, return projections
        """
        # a projection is a vector representing the span of a polygon projected
        # onto an axis
        # projections = []

        self.calc_shape_rotation()
        other.calc_shape_rotation()

        cdef double [2] axis
        cdef double [2] normalized

        cdef double [2] self_projection
        cdef double [2] other_projection


        for edge in chain(self._make_edges(), other._make_edges()):
            _normalize(edge, normalized)
            axis[0] = -normalized[0]
            axis[1] = normalized[1]

            # the separating axis is the line perpendicular to the edge
            _project(self.absolute_shape, axis, self_projection)
            _project(other.absolute_shape, axis, other_projection)

            # if self and other do not intersect on any axis, they do not
            # intersect in space
            if not _intersect(self_projection, other_projection):
                return False
            # find the overlapping portion of the projections
            # projection = self_projection[1] - other_projection[0]
            # projections.append((axis[0] * projection, axis[1] * projection))
        return True

    def _make_edges(self):
        points = self.absolute_shape

        for i, point in enumerate(points):
            next_point = points[(i + 1) % self.num_points] # x, y of next point in series
            # yield [point, next_point]
            yield [point[0] - next_point[0], point[1] - next_point[1]]
